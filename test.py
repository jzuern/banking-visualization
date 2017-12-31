import pandas as pd
import numpy as np
import ggplot

df = pd.DataFrame({
    "x": np.random.normal(0, 10, 1000),
    "y": np.random.normal(0, 10, 1000),
    "z": np.random.normal(0, 10, 1000)
})
df = pd.melt(df)

p = ggplot.ggplot(ggplot.aes(x='value', color='variable'), data=df)