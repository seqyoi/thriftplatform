import pandas as pd
import joblib
import os
import numpy as np
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from thrifty.models import Product


class Command(BaseCommand):
    help = "Train product recommenders"

    def handle(self, *args, **kwargs):
        # === Load and validate CSV ===
        csv_path = 'thrifty/data/products.csv'
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"❌ File not found: {csv_path}"))
            return

        try:
            df = pd.read_csv(csv_path)
            df.columns = df.columns.str.strip()
            df = df.dropna(subset=['product_id'])
            df['product_id'] = df['product_id'].astype(str).str.strip()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ CSV processing failed: {str(e)}"))
            return

        # === Get valid product IDs from DB ===
        db_ids = set(Product.objects.values_list('product_id', flat=True))

        # === Popularity-Based Recommendations ===
        if 'user_id' in df.columns:
            popular_df = df.groupby('product_id')['user_id'].nunique()
        else:
            popular_df = df['product_id'].value_counts()

        popular_ids = [
            str(pid).strip() for pid in popular_df.index
            if str(pid).strip() in db_ids
        ][:10]

        if not popular_ids:
            self.stdout.write(self.style.WARNING("⚠️ No valid popular products - using fallback"))
            popular_ids = list(Product.objects.values_list('product_id', flat=True)[:10])

        joblib.dump(popular_ids, 'thrifty/data/popular_df.pkl')
        self.stdout.write(f"✅ Saved {len(popular_ids)} popular products")

        # === Content-Based Recommendations ===
        recommendations = {}
        if {'product_name', 'category'}.issubset(df.columns):
            df['product_name'] = df['product_name'].astype(str)
            df['category'] = df['category'].astype(str)
            df['combined'] = df['product_name'].fillna('') + ' ' + df['category'].fillna('')

            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(df['combined'])
            cosine_sim = cosine_similarity(tfidf_matrix)

            df = df.drop_duplicates(subset='product_id').reset_index(drop=True)
            product_ids = df['product_id'].tolist()
            indices = pd.Series(df.index, index=df['product_id'])

            for pid in product_ids:
                if pid not in indices:
                    continue
                idx = indices[pid]
                sim_scores = list(enumerate(cosine_sim[idx]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

                recommended_ids = []
                for i, score in sim_scores:
                    if i >= len(df):
                        continue
                    other_pid = df.iloc[i]['product_id']
                    if other_pid != pid and other_pid not in recommended_ids:
                        recommended_ids.append(other_pid)
                    if len(recommended_ids) == 5:
                        break

                recommendations[pid] = recommended_ids

            joblib.dump(recommendations, 'thrifty/data/content_recommendations.pkl')
            self.stdout.write(f"✅ Saved content-based recommendations for {len(recommendations)} products")

        # === Collaborative Filtering (Item-based) ===
        if {'user_id', 'product_id'}.issubset(df.columns):
            interaction_df = df[['user_id', 'product_id']].dropna()
            interaction_df['user_id'] = interaction_df['user_id'].astype(str)
            interaction_df['product_id'] = interaction_df['product_id'].astype(str)

            pivot = interaction_df.pivot_table(
                index='user_id',
                columns='product_id',
                aggfunc=len,
                fill_value=0
            )

            item_sim = cosine_similarity(pivot.T)
            item_sim_df = pd.DataFrame(item_sim, index=pivot.columns, columns=pivot.columns)

            collab_recommendations = {}
            for pid in item_sim_df.columns:
                sim_scores = item_sim_df[pid].sort_values(ascending=False)
                top_similar = [other for other in sim_scores.index if other != pid][:5]
                collab_recommendations[pid] = top_similar

            joblib.dump(collab_recommendations, 'thrifty/data/collaborative_recommendations.pkl')
            self.stdout.write(f"✅ Saved collaborative recommendations for {len(collab_recommendations)} products")

        # === Save Product DataFrame for reference ===
        joblib.dump(df, 'thrifty/data/products_df.pkl')

        # === Done ===
        self.stdout.write(self.style.SUCCESS("🎯 Recommender training complete."))
