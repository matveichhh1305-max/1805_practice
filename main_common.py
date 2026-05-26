import matplotlib.pyplot as plt

# fig, ax = plt.subplots()
# ax.plot([1, 2, 3, 4], [1, 4, 2, 5])
# plt.ylabel('some numbers')
# plt.savefig('plot.png')

from sklearn.datasets import make_blobs
import pandas as pd
dataset, classes = make_blobs(
    n_samples=200,
    centers=4,
    n_features=2,
    cluster_std=0.5,
    random_state=0)

df = pd.DataFrame(dataset, columns=['var1', 'var2'])
print(df.head(2))

from yellowbrick.cluster import KElbowVisualizer
from sklearn.cluster import KMeans
model = KMeans()
visualizer = KElbowVisualizer(model, k=(1, 12)).fit(df)
visualizer.show(outpath="elbowobz.png")

kmeams = KMeans(n_clusters=4, init='k-means++', random_state=0).fit(df)
print(kmeams.labels_)
print(kmeams.cluster_centers_)
print(kmeams.inertia_)
print(kmeams.n_iter_)

# from collections  import Counter
# Counter(kmeams.labels_)
# print(Counter(kmeams.labels_))

# import seaborn as sns
# sns.scatterplot(data=df, x='var1', y='var2', hue=kmeams.labels_)
# plt.savefig('scatter.png')

# sns.scatterplot(data=df, x='var1', y='var2', hue=kmeams.labels_)
# plt.scatter(kmeams.cluster_centers_[:, 0], kmeams.cluster_centers_[:, 1], s=80, c='r', marker = "X", label='Centroids')
# plt.legend()
# plt.savefig('scatterX.png')