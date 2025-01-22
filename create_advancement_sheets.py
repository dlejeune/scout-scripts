from email.policy import default
import pandas as pd
import numpy as np
import argparse

class AdvancementUtils():
    FULL = True
    levels = ["Membership", "Traveller", "Discoverer", "1st Class", "Springbok"]
    themes = ["Safety", "Living Outdoors", "Adventure", "Scout Skills", "Service", "Personal Dev"]
    
    col_numbers = {
        0: "A",
        1: "B",
        2: "C",
        3: "D",
        4: "E",
        5: "F",
        6: "G",
        7: "H",
        8: "I",
        9: "J",
        10: "K",
    }

    def __init__(self):
        pass


    def create_advancement_sheets(self, in_file, out_file, full_export, export_style = "H"):
        in_df = self.read_sheet(in_file, full_export)
        if export_style == "H":
            pivot_df = self.pivot_names_horizontal(in_df)
        else:
            pivot_df = self.pivot_names_vertical(in_df)
        self.write_df(pivot_df, out_file)


    def trim_name(self, name_str):
        name_arr = name_str.split(" ")
        initial = name_arr[1][0:1]

        return "{} {}".format(name_arr[0], initial)


    def colour_rows(self, x):
        if x:
            return "background-color:black;color: black"
            
        else:
            return "background-color:white;color: white"


    def read_sheet(self, filename, full_export):

        df = pd.read_excel(filename)
        df = df.drop(["Age", "Invested", "End"], axis=1)
        df = pd.melt(df, id_vars=["Patrol", "Name"], var_name="Requirement", value_name="Passed")
        df.fillna(value = False, inplace=True)

        if not full_export:
            df.loc[df["Passed"] == "X", "Passed"] = True
        else:
            df[["Temp","DatePassed", "Scouter"]] = df["Passed"].str.split("\n", n=2, expand=True)
            df = df.drop(["Temp"], axis = 1)
            df.loc[df["Passed"] != False, "Passed"] = True
            df = df.replace({np.nan: None})

            df[df["DatePassed"]!= None]
            df["DatePassed"] = df["DatePassed"].str.extract(r"(\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$)", expand = False)[0]
            df["DatePassed"] = pd.to_datetime(df["DatePassed"])
            df["Scouter"] = df["Scouter"].str.slice(start = 3)
        
        df["Name"] = df["Name"].apply(lambda x: x[0:x.find("\n")])
        df["Name"] = df["Name"].apply(self.trim_name)
        df[["Level", "Requirement", "Theme"]] = df["Requirement"].str.split("\n", n=2, expand=True)

        df["Theme"] = df["Theme"].str.replace(' \(', '', regex=True)
        df["Theme"] = df["Theme"].str.replace('\)', '', regex=True)

        df[["Level", "Theme", "Patrol"]]= df[["Level", "Theme", "Patrol"]].astype("category")

        df["Level"] = df["Level"].cat.reorder_categories(["Membership", "Traveller", "Discoverer", "1st Class", "Springbok"])

        

        df["Theme"] = df["Theme"].cat.rename_categories({
            "Safety Awareness Theme": "Safety",
            "Living Outdoors Theme": "Living Outdoors",
            "Adventure Theme": "Adventure",
            "Skills Theme": "Scout Skills",
            "Service Theme": "Service",
            "Personal Development Theme": "Personal Dev"
        })


        df["Theme"] = df["Theme"].cat.reorder_categories(["Safety", "Living Outdoors", "Adventure", "Scout Skills", "Service", "Personal Dev", ""])


        adv_df = df.copy()

        return adv_df


    def pivot_names_horizontal(self, df):
        df = df.pivot(columns=["Patrol", "Name"], index = ["Level", "Theme", "Requirement"], values = "Passed")
        df = df.sort_index(axis = 1)

        return df.copy()
        

    def pivot_names_vertical(self, df):
        df = df.pivot(index=["Patrol", "Name"], columns = ["Level", "Theme", "Requirement"], values = "Passed")
        df = df.sort_index(axis = 1)

        return df.copy()


    def write_df(self, df, filename):
        writer = pd.ExcelWriter(filename, engine = "xlsxwriter")
        workbook = writer.book
        self.create_formats(workbook)

        for patrol in df.columns.get_level_values(0).categories.to_list():
            out_df = df.loc[:, (patrol)].copy()
            self.write_patrol(writer, out_df, patrol)
            
        writer.close()


    def create_formats(self, workbook):
        self.level_format = workbook.add_format({"bold": True, "font_size": 14, "font_name": "Verdana", "align": "center", "valign":"vcenter", "rotation":90})
        self.theme_format = workbook.add_format({"bold": True, "font_size": 12, "font_name": "Verdana", "align": "center", "valign":"vcenter", "rotation":90, "text_wrap": True})
        self.requirement_fmt = workbook.add_format({"font_size": 10, "font_name": "Verdana", "align": "horizontal", "valign":"vcenter"})
        self.true_format = workbook.add_format({"font_color": "black", "bg_color": "black"})
        self.false_format = workbook.add_format({"font_color": "white", "bg_color": "white"})
        self.header_format = workbook.add_format({"bold": True, "font_size": 9, "font_name": "Verdana", "align": "center", "valign":"vcenter", "text_wrap": True})
        self.border_format = workbook.add_format({"border": 1})
        self.title_format = workbook.add_format({"bold": True, "font_size": 20, "font_name": "Verdana", "align": "center", "valign":"vcenter"})


    def write_patrol(self, writer, patrol_df, patrol_name):
        ## Row in the spreadhseet where the header will go (0 indexed)
        first_row_df = 1
        
        ## Write the DF to the shete
        patrol_df = patrol_df.reset_index()
        patrol_name = patrol_name.replace("/", "-")
        patrol_df.to_excel(writer, sheet_name = patrol_name, index=False, startrow=first_row_df)

        last_col = self.col_numbers[len(patrol_df.columns.to_list())-1]

        ## Get the current sheet and set the page layout properties
        worksheet = writer.sheets[patrol_name]
        worksheet.set_portrait()
        worksheet.set_paper(8)
        worksheet.set_margins(0.25, 0.25, 0.25, 0.25)

        ## Merge the Advancement level rows
        start_row = first_row_df + 2
        for level in self.levels:
            end_row = start_row + len(patrol_df.loc[patrol_df.Level == level, :])
            worksheet.merge_range("A{}:A{}".format(start_row, end_row-1), level, self.level_format)
            start_row = end_row

        ## Merging theme rows
        worksheet.merge_range("B{}:B{}".format(first_row_df+2, first_row_df+7), "", self.theme_format)
        start_row =  first_row_df + 8 # inclusive
        for level in self.levels[1:]:
            for theme in self.themes:
                end_row = start_row + len(patrol_df.loc[(patrol_df.Level == level) & (patrol_df.Theme == theme), :])
                if end_row - start_row  > 1:
                    worksheet.merge_range("B{}:B{}".format(start_row, end_row-1), theme, self.theme_format)
                else:
                    worksheet.write("B{}".format(start_row), theme, self.theme_format)
                start_row = end_row

        ## Set the "index" column sizes and format
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 5)
        worksheet.set_column('C:C', 30, self.requirement_fmt)

        ## Add conditional formatting for the true/false cells, as well as borders (jank af)
        full_data_range = "A{}:{}{}".format(first_row_df+1, last_col, first_row_df+134)
        pass_range = "D{}:{}{}".format(first_row_df+2, last_col, first_row_df+134)

        worksheet.conditional_format(pass_range, {'type':     'cell',
                                                'criteria': '=',
                                                'value':    True,
                                                'format':   self.true_format})

        worksheet.conditional_format(pass_range, {'type':     'cell',
                                                'criteria': '=',
                                                'value':    False,
                                                'format':   self.false_format})

        worksheet.conditional_format(full_data_range, {"type": "no_blanks", "format": self.border_format})                                        

        
        ## Change the patrol member column width
        ## TODO: Make dynamic for num patrol members
        worksheet.set_column(4, len(patrol_df.columns.to_list())-4, 90//(len(patrol_df.columns.to_list())-3))


        ## Change row height
        for i in range(first_row_df+1, 135):
            worksheet.set_row_pixels(i, 25)


        ## Rewrite the header row, excluding first two columns
        header_to_write = patrol_df.columns.to_list()
        header_to_write[0] = " "
        header_to_write[1] = " "

        worksheet.write_row(first_row_df, 0, header_to_write)
        worksheet.set_row_pixels(first_row_df, 40, self.header_format)

        ## Write the title
        worksheet.set_row_pixels(0, 40)
        worksheet.merge_range("A1:{}1".format(last_col), "{} Advancement".format(patrol_name), self.title_format)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("infile")
    parser.add_argument("outfile")
    parser.add_argument("--fullexport", default = True,  action = argparse.BooleanOptionalAction)
    parser.add_argument("-v", action="store_true")

    args = parser.parse_args()

    utils = AdvancementUtils()

    pivot_direction = "V" if args.v else "H"
    

    utils.create_advancement_sheets(args.infile, args.outfile, args.fullexport, pivot_direction)