# -*- coding: utf-8 -*-
"""

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kKG4Vp4qu5wBacKWnCRsKKUuTJ9B1n4a
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sklearn.metrics as skm
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier, plot_tree
from IPython.core.display import display, HTML
from xgboost import XGBClassifier  
from sklearn.model_selection import GridSearchCV
import warnings 
warnings.filterwarnings(action= 'ignore')
# %matplotlib inline

data = pd.read_csv('/content/drive/Shareddrives/ML_DDR_Assignments_WinterQuarter/FINAL_GROUP_ML_PROJECT/heart_2020_cleaned.csv')
data.head()

data.info()

## check data imbalance
data.groupby('HeartDisease').size()

"""### **EDA**


"""

print(data[data["HeartDisease"] == "Yes"]['BMI'].min())
print(data[data["HeartDisease"] == "Yes"]['BMI'].max())

## Generally, BMI between 18.5 and 24.9 is the normal range. Any BMI value outside this range will be regarded as healthy risk. 
print('The percentage of people with heart disease and has a BMI value out of the normal range is {}.'.format(round(len(data[(data["HeartDisease"] == "Yes") & (data['BMI']<18.5)])/len(data[data["HeartDisease"] == "Yes"]),2)+
      round(len(data[(data["HeartDisease"] == "Yes") & (data['BMI']>24.9)])/len(data[data["HeartDisease"] == "Yes"]),2)))

## distribution of BMI
sns.boxplot(data['BMI'][data["HeartDisease"] == "Yes"])
plt.title("Frequency distribution of BMI of people with heart disease")
plt.show()

## for people who has heart disease, we want to know how the distribution of relevant features looks like
for col in data.columns[2:]:
    fig, ax = plt.subplots()
    data[col][data["HeartDisease"] == "Yes"].value_counts().plot.bar()
    plt.title(f"Frequency distribution of {col} rates\n"
              f"of people with heart disease")

"""### **Pre-processing**"""

## We can see that the data is highly imbalanced, with only 8.5% of the samples are with heart 
## disease. So, we apply bootstrapping to deal with the data imbalance.

HD_yes = data[data['HeartDisease'] == 'Yes']
HD_no = data[data['HeartDisease'] == 'No']

sample_yes = HD_yes.sample(n = 5000, replace=True, random_state=21)
sample_no = HD_no.sample(n = 5000, replace=True, random_state=21)

sample = pd.concat([sample_yes, sample_no])

print(sample.info())
sample.groupby('HeartDisease').size()

## convert the data type
le = LabelEncoder()
sample['HeartDisease'] = le.fit_transform(sample['HeartDisease'])
le_hd_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_hd_mapping)

# race = pd.get_dummies(sample['Race'])
# AgeCategory = pd.get_dummies(sample['AgeCategory'])
# PhysicalActivity = pd.get_dummies(sample['PhysicalActivity'])
# GenHealth = pd.get_dummies(sample['GenHealth'])

sample['Race'] = le.fit_transform(sample['Race'])
le_race_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_race_mapping)

sample['AgeCategory'] = le.fit_transform(sample['AgeCategory'])
le_age_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_age_mapping)

sample['Sex'] = le.fit_transform(sample['Sex'])
le_sex_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_sex_mapping)

sample['DiffWalking'] = le.fit_transform(sample['DiffWalking'])
le_df_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_df_mapping)

sample['Smoking'] = le.fit_transform(sample['Smoking'])
le_sk_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_sk_mapping)

sample['AlcoholDrinking'] = le.fit_transform(sample['AlcoholDrinking'])
le_ad_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_ad_mapping)

sample['Stroke'] = le.fit_transform(sample['Stroke'])
le_st_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_st_mapping)

sample['Diabetic'] = le.fit_transform(sample['Diabetic'])
le_db_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_db_mapping)

sample['PhysicalActivity'] = le.fit_transform(sample['PhysicalActivity'])
le_pa_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_pa_mapping)

sample['GenHealth'] = le.fit_transform(sample['GenHealth'])
le_gh_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_gh_mapping)

sample['Asthma'] = le.fit_transform(sample['Asthma'])
le_as_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_as_mapping)

sample['KidneyDisease'] = le.fit_transform(sample['KidneyDisease'])
le_kd_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_kd_mapping)

sample['SkinCancer'] = le.fit_transform(sample['SkinCancer'])
le_sc_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print(le_sc_mapping)

## Let us quickly check the heat map for sample dataset
plt.figure(figsize = (20,10))
sns.heatmap(sample.corr(),annot = True)
plt.show()

sample.head()

"""### **Model building**

Set up the train and test dataset
"""

## build the X and y
X = sample.loc[:, ~sample.columns.isin(['HeartDisease'])]
y = sample['HeartDisease']

## split the train-test dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=21)

"""Model 1: Logistic regression"""

## create Logistic Regression classifier, and train the model
logit = LogisticRegression()
logistic_base_model = logit.fit(X_train, y_train)

y_pred_logit = logit.predict(X_test)

## create boxplot to present the model
y_pred_prob = logit.predict_proba(X_train)[:, 1]
sns.set_palette("pastel")
sns.boxplot(x=y_train, y=y_pred_prob)
plt.xlabel('fitted probability of diabetes')
plt.show()

print(skm.classification_report(y_test, y_pred_logit))

## calculate the cross-validation score to further validate the model
cv_score = cross_val_score(logit, X_train, y_train, cv=5)
print('Average 5-fold CV score is {:2f}.'.format(np.mean(cv_score)))

## compute predicted probabilities
y_pred_prob = logit.predict_proba(X_test)[:, 1]
## generate ROC curve values: fpr, tpr, thresholds
fpr, tpr, thresholds = skm.roc_curve(y_test, y_pred_prob)

## plot the ROC curve
plt.plot([0,1], [0,1], 'k--')
plt.plot(fpr, tpr)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.show()

## calculate PR curve values: precision, recall, thresholds
precision, recall, thresholds = skm.precision_recall_curve(y_test, y_pred_prob)

## plot the PR curve
plt.plot([0,1], [0,1], 'k--')
plt.plot(recall, precision)
plt.ylabel('Precision')
plt.xlabel('Recall')
plt.title('PR Curve')
plt.show()

## calculate the PR-AUC value
auc_precision_recall = skm.auc(recall, precision)
roc_auc = skm.roc_auc_score(y_test, y_pred_prob)
print('The ROC-AUC score is: ', roc_auc)
print('The PR-AUC score is: ', auc_precision_recall)

"""Model 2: Random Forest"""

## create Random Forest classifier, and train the model 
## (for fair comparison purpose, we set the maximum depth = 6 for the model)
rf = RandomForestClassifier(max_depth=6, n_estimators=20)
rf_model = rf.fit(X_train, y_train)

## predict y using Random Forest classifier, and print out the classification report
y_pred_rf = rf_model.predict(X_test)
print(skm.classification_report(y_test, y_pred_rf))

## calculate the cross-validation score to further validate the model
cv_score = cross_val_score(rf, X_train, y_train, cv=5)
print('Average 5-fold CV score is {:2f}.'.format(np.mean(cv_score)))

## compute predicted probabilities
y_pred_prob = rf.predict_proba(X_test)[:, 1]
## generate ROC curve values: fpr, tpr, thresholds
fpr, tpr, thresholds = skm.roc_curve(y_test, y_pred_prob)

## plot the ROC curve
plt.plot([0,1], [0,1], 'k--')
plt.plot(fpr, tpr)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.show()

## calculate PR curve values: precision, recall, thresholds
precision, recall, thresholds = skm.precision_recall_curve(y_test, y_pred_prob)

## plot the PR curve
plt.plot([0,1], [0,1], 'k--')
plt.plot(recall, precision)
plt.ylabel('Precision')
plt.xlabel('Recall')
plt.title('PR Curve')
plt.show()

## calculate the PR-AUC value
auc_precision_recall = skm.auc(recall, precision)
roc_auc = skm.roc_auc_score(y_test, y_pred_prob)
print('The ROC-AUC score is: ', roc_auc)
print('The PR-AUC score is: ', auc_precision_recall)

"""Model 3: XGBoosting"""

## create XGBoosting classifier, and train the model
xgb = XGBClassifier(max_depth=6, n_estimators=20)
xgb_model = xgb.fit(X_train, y_train)

## predict y using XGBoosting classifier, and print out the classification report
y_pred_xgb = xgb_model.predict(X_test)
print(skm.classification_report(y_test, y_pred_xgb))

## calculate the cross-validation score to further validate the model
cv_score = cross_val_score(xgb, X_train, y_train, cv=5)
print('Average 5-fold CV score is {:2f}.'.format(np.mean(cv_score)))

## compute predicted probabilities
y_pred_prob = xgb.predict_proba(X_test)[:, 1]
## generate ROC curve values: fpr, tpr, thresholds
fpr, tpr, thresholds = skm.roc_curve(y_test, y_pred_prob)

## plot the ROC curve
plt.plot([0,1], [0,1], 'k--')
plt.plot(fpr, tpr)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.show()

## calculate PR curve values: precision, recall, thresholds
precision, recall, thresholds = skm.precision_recall_curve(y_test, y_pred_prob)

## plot the PR curve
plt.plot([0,1], [0,1], 'k--')
plt.plot(recall, precision)
plt.ylabel('Precision')
plt.xlabel('Recall')
plt.title('PR Curve')
plt.show()

## calculate the PR-AUC value
auc_precision_recall = skm.auc(recall, precision)
roc_auc = skm.roc_auc_score(y_test, y_pred_prob)
print('The ROC-AUC score is: ', roc_auc)
print('The PR-AUC score is: ', auc_precision_recall)

"""### **XGBoosting Model tuning**"""

## as XGBoosting is the best model, we do a grid search on it to further improve the model performance

#Perform grid of parameters
parameters = {'nthread':[4], #when use hyperthread, xgboost may become slower
              'learning_rate': [0.05,0.1],
              'max_depth': [6,7,8],
              'min_child_weight': [11],
              'subsample': [0.5,0.8],
              'colsample_bytree': [0.5,0.7],
              'n_estimators': [10,15,20],
              'seed': [1]}
grid_xgb=GridSearchCV(estimator=xgb, param_grid=parameters, scoring='f1', cv=5, n_jobs=-1)
grid_xgb.fit(X_train, y_train)

## print out the best parameters of the XGBoosting grid search
print(grid_xgb.best_params_)

## build up the best XGBoosing model
best_xgb=XGBClassifier(colsample_bytree=0.7, learning_rate=0.1, max_depth=7, min_child_weight=11, n_estimators=20, nthread=4, seed=1, subsample=0.8)
best_xgb_model = best_xgb.fit(X_train, y_train)

## predict y using XGBoosting classifier, and print out the classification report
y_pred_xgb = best_xgb_model.predict(X_test)
print(skm.classification_report(y_test, y_pred_xgb))

## compute predicted probabilities
y_pred_prob = best_xgb_model.predict_proba(X_test)[:, 1]
## generate ROC curve values: fpr, tpr, thresholds
fpr, tpr, thresholds = skm.roc_curve(y_test, y_pred_prob)

## plot the ROC curve
plt.plot([0,1], [0,1], 'k--')
plt.plot(fpr, tpr)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.show()

## calculate PR curve values: precision, recall, thresholds
precision, recall, thresholds = skm.precision_recall_curve(y_test, y_pred_prob)

## plot the PR curve
plt.plot([0,1], [0,1], 'k--')
plt.plot(recall, precision)
plt.ylabel('Precision')
plt.xlabel('Recall')
plt.title('PR Curve')
plt.show()

## calculate the PR-AUC value
auc_precision_recall = skm.auc(recall, precision)
roc_auc = skm.roc_auc_score(y_test, y_pred_prob)
print('The ROC-AUC score is: ', roc_auc)
print('The PR-AUC score is: ', auc_precision_recall)

## print out the FEATURE IMPORTANCE according to the XGBoosting model
importance_xgb = pd.Series(best_xgb.feature_importances_, index=X_train.columns)

sorted_importance_xgb = importance_xgb.sort_values()

sorted_importance_xgb.plot(kind='barh', color='lightgreen')
plt.show()
