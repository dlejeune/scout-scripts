import pandas as pd


## Read in the trash spreadhseet
df = pd.read_excel("data.xlsx")

## Drop Useless columns
df = df.drop(["Age", "Patrol", "Invested", "End"], axis=1)

## Convert to long format
df = pd.melt(df, id_vars=["Name"], var_name="Requirement", value_name="Passed")

## Change values to booleans
df.loc[df["Passed"] == "X", "Passed"] = True
df.fillna(value = False, inplace=True)

## Split horrendous naming convention into meaningful colunmns
df["Name"] = df["Name"].apply(lambda x: x[0:x.find("\n")])
df[["Level", "Requirement", "Theme"]] = df["Requirement"].str.split("\n", 2, expand=True)


## Revert to long format
df = df.pivot(columns="Name", index = ["Level", "Theme", "Requirement"], values = "Passed")

## Some more string manipulation
df.index = df.index.set_levels(df.index.levels[1].str.replace(' \(', ''), level=1)
df.index = df.index.set_levels(df.index.levels[1].str.replace('\)', ''), level=1)

## Export
df.to_excel("out.xlsx")