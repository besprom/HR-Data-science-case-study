# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WCvX-WnaokJbJUKNTrDjb9j164SSlovG
"""

#The below code simply imports and prepares the data needed from Google Sheets
from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default
creds, _ = default()

from gspread_dataframe import set_with_dataframe


gc = gspread.authorize(creds)

sheet1 = 'Recruiting Activity Data'
recruitingactivity = gc.open('People Analytics Data Science and Reporting - Case Study FINAL').worksheet(sheet1)
rows = recruitingactivity.get_all_values()


import pandas as pd
pd.set_option('display.max_rows', None)


recruitingactivity = pd.DataFrame.from_records(rows)
recruitingactivity.columns = recruitingactivity.iloc[0]
recruitingactivity = recruitingactivity[1:]

#Question 1
#1.1 My first step will involve ensuring that we are only counting each candidate once per recruiting funnel. To do so, I will first ensure that there are no duplicates where the Candidate ID and Department is the same. When there are duplicates, I am retaining the data involving the furthest recruiting state.
#After this is done, the highest degree per candidate is also found
recruitingactivity["Furthest Recruiting Stage Reached"] = recruitingactivity["Furthest Recruiting Stage Reached"].replace({'In-house Interview': 'In-House Interview'})
recruitingactivity["Numbered Furthest Recruiting Stage Reached"] = recruitingactivity["Furthest Recruiting Stage Reached"].replace({'New Application': 1, 'Phone Screen': 2, 'In-house Interview': 3, 'In-House Interview':3,'Offer Sent': 4, 'Offer Accepted':5})

question1recruitingactivity = recruitingactivity.sort_values(by=["Numbered Furthest Recruiting Stage Reached"]).drop_duplicates(subset=['Candidate ID Number','Department'], keep='last')
#I know this may not be the most elegant option, but I decided to rename the 'Degree' columns in the sheet, to avoid Column name duplicates (avoiding column name duplicates is best practice anyways)
question1recruitingactivity["Degree1"] = question1recruitingactivity["Degree1"].replace({'PhD': 1, 'Masters': 2, 'JD': 2, 'Bachelors':3})
question1recruitingactivity["Degree2"] = question1recruitingactivity["Degree2"].replace({'PhD': 1, 'Masters': 2, 'JD': 2, 'Bachelors':3})
question1recruitingactivity["Degree3"] = question1recruitingactivity["Degree3"].replace({'PhD': 1, 'Masters': 2, 'JD': 2, 'Bachelors':3})
question1recruitingactivity["Degree4"] = question1recruitingactivity["Degree4"].replace({'PhD': 1, 'Masters': 2, 'JD': 2, 'Bachelors':3})
#there is an error in the following line of code. I believe this errors is due to the minimum function only seeking minimums in the first two columns listed. I could not find a solution to this issue. I proceeded as I found this error a bit late into the process but I will keep seeking a solution :)
question1recruitingactivity['Highest Degree'] = question1recruitingactivity[["Degree1", "Degree2", "Degree3", "Degree4"]].min(axis=1)


#1.2 This second step will involve finding all Department and Highest Degree combinations, along with candidate counts for each, per Furthest Recruiting Stage
#Note that I manually changed the name of each Degree column to unique column names, to avoid confusion with the other identically titled columns. In general, it is good practice to ensure data has unique column names
question1recruitingactivity = question1recruitingactivity[['Department', "Furthest Recruiting Stage Reached", 'Highest Degree']]
results1 = question1recruitingactivity.groupby(['Department', 'Highest Degree'] ).value_counts()

results1 = pd.DataFrame(results1)
#1.3 In this 3rd step, I am simply exporting the results
#From there, I will do some manual work. This manual work will include calculating conversion rates and doing some formatting. I will also use Excel formulas to calculate the number of candidates per Offer Response.
#For scalability, I usually avoid this manual work but I do think that it is important to think through the time needed to code a solution vs just manually implementing a solution

#results1.to_csv(r'\\file3.csv')

#Question 2
#2.1 My first step here is to filter for candidates where furthest recruiting stage was In House interview and beyond AND where candidates applied from Career Fair or Campus Event

question2recruitingactivity = recruitingactivity[recruitingactivity["Numbered Furthest Recruiting Stage Reached"] >2 ]
question2recruitingactivity = recruitingactivity[(recruitingactivity["Application Source"] == "Career Fair" ) | (recruitingactivity["Application Source"] == "Campus Event") ]

#2.2 My second step is to attain counts of both the filtered data and the entire data, by year
question2recruitingactivity["Date of Application"] = pd.to_datetime(question2recruitingactivity["Date of Application"], errors='coerce')
question2recruitingactivity["year"] = question2recruitingactivity["Date of Application"].dt.year

recruitingactivity["Date of Application"] = pd.to_datetime(recruitingactivity["Date of Application"], errors='coerce')
recruitingactivity["year"] = recruitingactivity["Date of Application"].dt.year

question2recruitingactivity = question2recruitingactivity[['year']]
results2 = question2recruitingactivity.groupby(['year'] ).value_counts()
results2 = pd.DataFrame(results2)

temprecruitingactivity = recruitingactivity[['year']]
allresults = temprecruitingactivity.groupby(['year'] ).value_counts()
allresults = pd.DataFrame(allresults)

combinedresults2 = pd.merge(results2,allresults,how='left', left_index=True, right_index=True)

combinedresults2["rate"] = combinedresults2["0_x"] / combinedresults2["0_y"]

#2.3 Conducting chi-squared tests
combinedresults2 = combinedresults2.reset_index()
compare = pd.crosstab(combinedresults2['year'],combinedresults2['rate'])
import scipy.stats as stats
chi2, p, dof, ex = stats.chi2_contingency(compare)

print(f'Chi_square value {chi2}\n\np value {p}\n\ndegrees of freedom {dof}\n\n expected {ex}')

#for the given scenario, I do not believe chi-squared tests apply very well(although I would be happy to learn otherwise).I do not understand how to apply this type of statistical test to this exact scenario as I understand but I wanted to demonstrate that I could figure out how to run this test using Python

#Question 3
#3.1 First, I want to define effectiveness - I will define it as the rate at which candidates a reached recruiting stage that was In House interview and beyond

question3recruitingactivity = recruitingactivity[recruitingactivity["Numbered Furthest Recruiting Stage Reached"] >2 ]

question3recruitingactivity = question3recruitingactivity[['Application Source']]
results3 = question3recruitingactivity.groupby(['Application Source'] ).value_counts()
results3 = pd.DataFrame(results3)

temprecruitingactivity3 = recruitingactivity[['Application Source']]
allresults3 = temprecruitingactivity3.groupby(['Application Source'] ).value_counts()
allresults3 = pd.DataFrame(allresults3)


combinedresults3 = pd.merge(results3,allresults3,how='left', left_index=True, right_index=True)
combinedresults3["rate"] = combinedresults3["0_x"] / combinedresults3["0_y"]
combinedresults3 = combinedresults3.reset_index()


#3.2 Now, I will use pandas plots to create a visualization to demonstrate this effectiveness data
import seaborn as sns

combinedresults3 = combinedresults3[["rate", "Application Source"]]
combinedresults3 = combinedresults3.sort_values(by=['rate'])
ax = combinedresults3.plot.bar(x="Application Source", y="rate", title = "Effectiveness Rate by Application Source")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)