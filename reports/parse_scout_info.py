import pandas as pd
import typer 
from pathlib import Path

app = typer.Typer()

def extract_scout_info(df):
    
    df = df.drop(["Actions", "Image"], axis=1)
    df[["Name", "ID", "Account", "Contact"]
    ] = df["Name"].str.split("|", n=3, expand=True)
    df[["Temp1", "Temp2", "dob"]] = df["Age"].str.split(
        r"(\sDOB:\s)", n=1, expand=True)
    df = df.drop(["Temp1", "Temp2", "Account"], axis=1)
    df["dob"] = pd.to_datetime(df["dob"])

    df[["Email", "Phone"]] = df["Contact"].str.split("|", n=2, expand=True)
    df = df.drop(["Contact"], axis=1)

    df[["DateInvested", "Temp1"]] = df["Invested"].str.split(
        "|", n=0, expand=True)

    df.loc[df["DateInvested"] == "Not Invested ", "DateInvested"] = "2023-12-10"
    df = df.drop(["Temp1"], axis=1)

    # df[["Patrol", "Temp1"]] = df["Patrol"].str.split("|", 0, expand=True)
    # df = df.drop(["Temp1"], axis=1)

    df = df.drop(["Age", "Invested"], axis=1)

    df[["Name", "Surname"]] = df["Name"].str.split(" ", n=1, expand=True)

    df[["Patrol", "Role", "Gender"]] = df[[
        "Patrol", "Role", "Gender"]].astype("category")

    role_order = ['Patrol Member']

    if "Patrol Leader" in df["Role"].cat.categories:
        role_order.insert(0, "Patrol Leader")

    if "Troop Leader" in df["Role"].cat.categories:
        role_order.insert(0, "Troop Leader")

    if "Assistant Patrol Leader" in df["Role"].cat.categories:
        role_order.append("Assistant Patrol Leader")

    df["Role"] = df["Role"].cat.reorder_categories(
        role_order)

    df["FullName"] = df["Name"] + " " + df["Surname"]

    df = df.sort_values(by=["Patrol", "Role", "dob"],
                        ascending=[True, True, False])

    df["ID"] = df["ID"].str.strip()
    
    df = df[["FullName", "Patrol", "Gender", "Role", "Email", "ID", "Name", "Surname", "Phone", "dob", "DateInvested"]]

    return df.copy()

@app.command("fromfile")
def cli_extract_info(input_file: Path, output_file: Path):
    df = pd.read_excel(input_file)
    out_df = extract_scout_info(df)
    out_df.to_excel(output_file, index=False)

@app.command("cb")
def cli_extract_info_from_clipboard():
    df = pd.read_clipboard()
    out_df = extract_scout_info(df)
    out_df.to_clipboard(index=False)
    
    

if __name__ == "__main__":
    app()