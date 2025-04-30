
import pandas as pd
from sklearn.datasets import load_iris
import matplotlib.pyplot as plt 
import seaborn as sns


iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['species'] = iris.target_names[iris.target]

print("=== Dataset Preview ===")
print(df.head())

print("\n=== Dataset Info ===")
print(df.info())

print("\n=== Basic Statistics ===")
print(df.describe())

print("\n=== Mean Sepal Length by Species ===")
print(df.groupby('species')['sepal length (cm)'].mean())

sns.set(style="whitegrid")


plt.figure(figsize=(10, 5))
df[:30].plot(y='sepal length (cm)', title='Sepal Length Trend')
plt.savefig('line_chart.png') 
plt.show()

plt.figure(figsize=(8, 5))
sns.barplot(x='species', y='sepal length (cm)', data=df)
plt.title('Average Sepal Length by Species')
plt.savefig('bar_chart.png')
plt.show()

plt.figure(figsize=(8, 5))
sns.histplot(data=df, x='petal length (cm)', hue='species', kde=True)
plt.title('Petal Length Distribution')
plt.savefig('histogram.png')
plt.show()


plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x='sepal length (cm)', y='petal length (cm)', hue='species')
plt.title('Sepal vs Petal Length')
plt.savefig('scatter_plot.png')
plt.show()