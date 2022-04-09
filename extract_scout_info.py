import pandas as pd
import numpy as np

def trim_name(name_str):
    name_arr = name_str.split(" ")
    initial = name_arr[1][0:1]

    return "{} {}".format(name_arr[0], initial)

def extract_scout_info():

    df = pd.read_excel("data.xlsx")
    df = df.drop(["Actions", "Image"], axis = 1)
    df[["Name", "ID", "Account", "Contact"]] = df["Name"].str.split("|", 3, expand = True)
    df[["Temp1", "Temp2", "dob"]] = df["Age"].str.split(r"(\sDOB:\s)", 1, expand = True)
    df = df.drop(["Temp1", "Temp2"], axis = 1)
    df["dob"] = pd.to_datetime(df["dob"])

    df[["Email", "Phone"]] =  df["Contact"].str.split("|", 2, expand = True)
    df = df.drop(["Contact"], axis = 1)

    df[["DateInvested", "Temp1"]] = df["Invested"].str.split("|", 0, expand = True)
    df = df.drop(["Temp1"], axis = 1)



    df[["Patrol", "Temp1"]] = df["Patrol"].str.split("|", 0, expand = True)
    df = df.drop(["Temp1"], axis = 1)


    df = df.drop(["Age", "Invested"], axis = 1)

    df[["Name", "Surname"]] = df["Name"].str.split(" ", 1, expand = True)

    df[["Patrol", "Role", "Gender"]]= df[["Patrol", "Role", "Gender"]].astype("category")

    df["Role"] = df["Role"].cat.reorder_categories(['Patrol Leader', 'Patrol Member', 'Assistant Patrol Leader'])

    df["Role"].cat.categories

    df["FullName"] = df["Name"] + " " + df["Surname"]

    df = df.sort_values(by = ["Patrol", "Role", "dob"], ascending = [True, True, False])


    return df.copy()



if __name__ == "__main__":
    out_df = extract_scout_info()[["Name", "Surname", "FullName", "Patrol", "Gender", "DateInvested", "dob", "Email", 'Phone', 'Role', 'ID', 'Account']]
    out_df.to_clipboard()
