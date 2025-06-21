import pandas as pd
import joblib
import os
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from thrifty.models import Product  # Added import

class Command(BaseCommand):
    help = "Train product recommenders"

    def handle(self, *args, **kwargs):
        # Load and validate data
        csv_path = 'thrifty/data/products.csv'
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"❌ File not found: {csv_path}"))
            return

        try:
            df = pd.read_csv(csv_path)
            df.columns = df.columns.str.strip()
            df = df.dropna(subset=['product_id'])
            df['product_id'] = df['product_id'].astype(str).str.strip()  # Ensure string IDs
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ CSV processing failed: {str(e)}"))
            return

        # Get existing product IDs from DB
        db_ids = set(Product.objects.values_list('product_id', flat=True))
        
        # Popularity recommendations
        if 'user_id' in df.columns:
            popular_df = df.groupby('product_id')['user_id'].nunique()
        else:
            popular_df = df['product_id'].value_counts()
        
        # Filter only products that exist in DB
        popular_ids = [
            str(pid).strip() for pid in popular_df.index 
            if str(pid).strip() in db_ids
        ][:10]  # Top 10
        
        if not popular_ids:
            self.stdout.write(self.style.WARNING("⚠️ No valid popular products - using fallback"))
            popular_ids = list(Product.objects.values_list('product_id', flat=True)[:10])
        
        joblib.dump(popular_ids, 'thrifty/data/popular_df.pkl')
        self.stdout.write(f"✅ Saved {len(popular_ids)} popular products")

        # Content-based recommendations
        if {'product_name', 'category'}.issubset(df.columns):
            df['product_name'] = df['product_name'].astype(str)
            df['category'] = df['category'].astype(str)
            df['combined'] = df['product_name'].fillna('') + ' ' + df['category'].fillna('')

            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(df['combined'])
            cosine_sim = cosine_similarity(tfidf_matrix)

            df['product_id'] = df['product_id'].astype(str).str.strip()
            df = df.drop_duplicates(subset='product_id').reset_index(drop=True)
            product_ids = df['product_id'].tolist()
            indices = pd.Series(df.index, index=df['product_id'])

            # === 5. Build full recommendation dictionary ===
           
            recommendations = {}
            for pid in product_ids:
                if pid not in indices:
                    continue  # skip if index not found
                idx = indices[pid]
                sim_scores = list(enumerate(cosine_sim[idx]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                
                recommended_ids = []
                for i, score in sim_scores:
                    if i >= len(df):  # avoid out-of-bounds
                        continue
                    other_pid = df.iloc[i]['product_id']
                    if other_pid != pid and other_pid not in recommended_ids:
                        recommended_ids.append(other_pid)
                    if len(recommended_ids) == 5:
                        break

                recommendations[pid] = recommended_ids


            joblib.dump(recommendations, 'thrifty/data/content_recommendations.pkl')
            joblib.dump(df, 'thrifty/data/products_df.pkl')
            self.stdout.write(f"✅ Saved content-based recommendations for {len(recommendations)} products")
            self.stdout.write(self.style.SUCCESS("🎯 Recommender training complete."))
