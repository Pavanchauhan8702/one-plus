# -*- coding: utf-8 -*-
"""telco-customer-churn-prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1r5nQy4-XcBaSUPQCg3ZQuqNtKGse2ib7
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LassoCV
from sklearn.feature_selection import SelectKBest, chi2

"""## Importing Dataset"""

df = pd.read_csv('/content/WA_Fn-UseC_-Telco-Customer-Churn.csv')
df.head()

df.dropna(inplace=True)

df.info()

df.describe()

plt.matshow(df.corr())

"""## Splitting dataset into X(features) and y(labels)"""

X=df.iloc[:,1:-1]
X.head()

y=df["Churn"]
y=pd.DataFrame(y)
y.head()

from sklearn.preprocessing import LabelEncoder
y=LabelEncoder().fit_transform(y)
# X=LabelEncoder().fit_transform(X)

X['gender']=LabelEncoder().fit_transform(X['gender'])
X['Partner']=LabelEncoder().fit_transform(X['Partner'])
X['Dependents']=LabelEncoder().fit_transform(X['Dependents'])
X['PhoneService']=LabelEncoder().fit_transform(X['PhoneService'])
X['MultipleLines']=LabelEncoder().fit_transform(X['MultipleLines'])
X['InternetService']=LabelEncoder().fit_transform(X['InternetService'])
X['OnlineSecurity']=LabelEncoder().fit_transform(X['OnlineSecurity'])
X['OnlineBackup']=LabelEncoder().fit_transform(X['OnlineBackup'])
X['DeviceProtection']=LabelEncoder().fit_transform(X['DeviceProtection'])
X['StreamingTV']=LabelEncoder().fit_transform(X['StreamingTV'])
X['StreamingMovies']=LabelEncoder().fit_transform(X['StreamingMovies'])
X['Contract']=LabelEncoder().fit_transform(X['Contract'])
X['PaperlessBilling']=LabelEncoder().fit_transform(X['PaperlessBilling'])
X['PaymentMethod']=LabelEncoder().fit_transform(X['PaymentMethod'])
X['TechSupport']=LabelEncoder().fit_transform(X['TechSupport'])
X['TechSupport']=LabelEncoder().fit_transform(X['TechSupport'])

y

X

X['MonthlyCharges'] = X['MonthlyCharges'].astype('int')

X['TotalCharges'] = pd.to_numeric(X['TotalCharges'],errors='coerce')
median = X['TotalCharges'].median()
X['TotalCharges'].fillna(median,inplace=True)

"""## Feature Selection

### Lasso
"""

reg = LassoCV()
reg.fit(X, y)
print("Best alpha using built-in LassoCV: %f" % reg.alpha_)
print("Best score using built-in LassoCV: %f" %reg.score(X,y))
coef = pd.Series(reg.coef_, index = X.columns)
print("Lasso picked " + str(sum(coef != 0)) + " variables and eliminated the other " + str(sum(coef == 0)) + " variables")

imp_coef = coef.sort_values()
import matplotlib
matplotlib.rcParams['figure.figsize'] = (6,6)
imp_coef.plot(kind = "barh")
plt.title("Feature importance using Lasso Model")
plt.show()

"""## Normalisation of data"""

from sklearn.preprocessing import MinMaxScaler
names=X.columns
indexes=X.index
X=MinMaxScaler().fit_transform(X)
X=pd.DataFrame(X,columns=names,index=indexes)
X.head()

"""### Select KBest using Chi2"""

kmodel=SelectKBest(score_func=chi2,k=8)
x_clf_new=kmodel.fit_transform(X,y)
mask=kmodel.get_support()
important=X.columns[mask]
print(important,len(important))

"""## Split data into train, test and validation set"""

from sklearn.model_selection import train_test_split
X_train,X_rem,y_train,y_rem = train_test_split(X, y, test_size=0.20, random_state=42)
X_val,X_test,y_val,y_test = train_test_split(X_rem, y_rem, test_size=0.50, random_state=42)

"""## Logistic Regression"""

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
log = LogisticRegression()
log.fit(X_train,y_train)
acc = accuracy_score(log.predict(X_val),y_val)
f'Validation accuracy: {round(acc*100,2)}%'

acc = accuracy_score(log.predict(X_test),y_test)
f'Testing accuracy: {round(acc*100,2)}%'

"""## Using top 3 variables given by LassoCV"""

log.fit(X_train[["MonthlyCharges","TotalCharges","tenure"]],y_train)
acc = accuracy_score(log.predict(X_val[["MonthlyCharges","TotalCharges","tenure"]]),y_val)
f'Validation accuracy: {round(acc*100,2)}%'

acc = accuracy_score(log.predict(X_test[["MonthlyCharges","TotalCharges","tenure"]]),y_test)
f'Testing accuracy: {round(acc*100,2)}%'

"""## Using top 8 variables given by Select Kbest"""

log.fit(X_train[['SeniorCitizen', 'Dependents', 'tenure', 'OnlineSecurity','OnlineBackup', 'TechSupport', 'Contract', 'PaperlessBilling']],y_train)
acc = accuracy_score(log.predict(X_val[['SeniorCitizen', 'Dependents', 'tenure', 'OnlineSecurity','OnlineBackup', 'TechSupport', 'Contract', 'PaperlessBilling']]),y_val)
f'Validation accuracy: {round(acc*100,2)}%'

acc = accuracy_score(log.predict(X_test[['SeniorCitizen', 'Dependents', 'tenure', 'OnlineSecurity','OnlineBackup', 'TechSupport', 'Contract', 'PaperlessBilling']]),y_test)
f'Testing accuracy: {round(acc*100,2)}%'

"""## Hyperparameter Tuning using GridSearchCV for decision tree"""

from sklearn.tree import DecisionTreeClassifier, export_graphviz, ExtraTreeClassifier, plot_tree
from sklearn.model_selection import GridSearchCV
def dtree_grid_search(X,y,nfolds):
    #create a dictionary of all values we want to test
    param_grid = { 'criterion':['gini','entropy'],'max_depth': np.arange(3, 15),'max_leaf_nodes': list(range(2, 10)), 'min_samples_split': [2, 3, 4]}
    # decision tree model
    dtree_model=DecisionTreeClassifier()
    #use gridsearch to test all values
    dtree_gscv = GridSearchCV(dtree_model, param_grid, cv=nfolds)
    #fit model to data
    dtree_gscv.fit(X, y)
    return dtree_gscv.best_params_

dtree_grid_search(X_train,y_train,2)

"""## Decision Tree Classifier"""

dt = DecisionTreeClassifier(criterion='entropy',max_depth=3)
dt = dt.fit(X_train,y_train)
y_pred = dt.predict(X_train)
acc = accuracy_score(y_train,y_pred)
f'Training accuracy: {round(acc*100,2)}%'

y_pred = dt.predict(X_val)
acc = accuracy_score(y_val,y_pred)
f'Validation accuracy: {round(acc*100,2)}%'

y_pred = dt.predict(X_test)
acc = accuracy_score(y_test,y_pred)
f'Testing accuracy: {round(acc*100,2)}%'

plot_tree(dt)

"""## Using features of GridSearchCV"""

dt = DecisionTreeClassifier(criterion= 'gini',
 max_depth= 5,
 max_leaf_nodes= 7,
 min_samples_split= 2)
dt = dt.fit(X_train,y_train)
y_pred = dt.predict(X_train)
acc = accuracy_score(y_train,y_pred)
f'Training accuracy: {round(acc*100,2)}%'

y_pred = dt.predict(X_val)
acc = accuracy_score(y_val,y_pred)
f'Validation accuracy: {round(acc*100,2)}%'

y_pred = dt.predict(X_test)
acc = accuracy_score(y_test,y_pred)
f'Testing accuracy: {round(acc*100,2)}%'

"""## Random Forest Classifier"""

from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=100, random_state=0)

rf.fit(X_train,y_train)
y_pred = dt.predict(X_train)
acc = accuracy_score(y_train,y_pred)
f'Training accuracy: {round(acc*100,2)}%'

y_pred = rf.predict(X_val)
acc = accuracy_score(y_val,y_pred)
f'Validation accuracy: {round(acc*100,2)}%'

y_pred = rf.predict(X_test)
acc = accuracy_score(y_test,y_pred)
f'Testing accuracy: {round(acc*100,2)}%'

"""## Using features of GridSearchCV"""

rf1 = RandomForestClassifier()
param_grid = [
 {'n_estimators': [10, 50, 100], 'max_features': [2, 4, 6, 8,12,14,16,18,20]},
 {'bootstrap': [False], 'n_estimators': [3, 10], 'max_features': [2, 3, 4]}]
grid_search = GridSearchCV(rf1, param_grid,scoring='accuracy',return_train_score=False)
grid_search.fit(X_train, y_train)

grid_search.best_params_

rf2 = RandomForestClassifier(max_features= 4, n_estimators= 100, random_state=0)
rf2.fit(X_train,y_train)
y_pred = rf2.predict(X_train)
acc = accuracy_score(y_train,y_pred)
f'Training accuracy: {round(acc*100,2)}%'

y_pred = rf2.predict(X_val)
acc = accuracy_score(y_val,y_pred)
f'Validation accuracy: {round(acc*100,2)}%'

y_pred = rf2.predict(X_test)
acc = accuracy_score(y_test,y_pred)
f'Testing accuracy: {round(acc*100,2)}%'

"""## The Telco Customer Churn is best predicted using Logistic Regression which has a testing accuracy of 82.14%"""