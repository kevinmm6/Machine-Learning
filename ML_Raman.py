# 10/03/20
# Kevin Marroquin
# Code using machine learning models on Raman data for pulp.
# %% Libraries setup
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.metrics import mean_squared_error
#%% Load and explore data
feature_filename='Raman 20200218.csv'
target_filename='Targets 20200218.csv'
features_dataset = pd.read_csv(feature_filename)
target_dataset=pd.read_csv(target_filename)
#First 48 pixels are blank so we're only gonna take pixels from 049-1024 as features
spectra_names = ["Spectrum_0"+str(ii) if ii<100 else "Spectrum_"+str(ii) for ii in range(49,1025)]
feature_data=features_dataset[spectra_names]
#The targer dataset is bigger than the features one and has nonvalues so we concatenate the two and delete the rows with NaN.
target_names=["Burst","BL","Tear"]
target_data=target_dataset[target_names]
dataset = pd.concat([feature_data,target_data],axis=1)
#Drop NaN values
dataset = dataset.dropna()
#%% Set training and validation dataset with burst target
X = dataset[spectra_names].values
y = dataset["Burst"].values
#Leave 20% of data for validation purposes
validation_size=0.20
seed = 7
train_X,val_X, train_y, val_y = train_test_split(X,y,test_size=validation_size,random_state=seed)
#%% Spot checking algorithms
models=[]
models.append(("LR",LinearRegression()))
models.append(("LASSO",Lasso()))
models.append(("EN",ElasticNet()))
models.append(("KNN",KNeighborsRegressor()))
models.append(("CART",DecisionTreeRegressor()))
models.append(("SVR",SVR()))
#Evaluate models using k-fold cross validation
n_folds=10
scoring_metric='neg_mean_squared_error'
results=[]
means=[]
std=[]
model_names=[ii for ii,_ in models]
for name,model in models:
    kfold=KFold(n_splits=n_folds,random_state=seed,shuffle=True)
    cv_results=cross_val_score(model,train_X,train_y,cv=kfold,scoring=scoring_metric)
    results.append(cv_results)
    means.append(cv_results.mean())
    std.append(cv_results.std())
    print("{}: {} ({})".format(name,cv_results.mean(),cv_results.std()))
plt.figure(1)
plt.boxplot(results,labels=model_names)
#%% Tunning 
#KNN
k_values=np.arange(1,21,2)
knn_grid_params={"n_neighbors":k_values}
knn_model=KNeighborsRegressor()
knn_grid=GridSearchCV(estimator=knn_model,param_grid=knn_grid_params,scoring=scoring_metric,cv=kfold)
knn_grid_results=knn_grid.fit(train_X,train_y)
print("Best value: {} with {}".format(knn_grid_results.best_score_,knn_grid_results.best_params_))
knn_grid_means=knn_grid_results.cv_results_['mean_test_score']
knn_grid_std=knn_grid_results.cv_results_['std_test_score']
knn_grid_params=knn_grid_results.cv_results_['params']
for ii in range(0,knn_grid_means.size):
    print('{:.5f} ({:.5f}) with {}'.format(knn_grid_means[ii],knn_grid_std[ii],knn_grid_params[ii]))
#%% Ensembles
ensembles=[]
ensembles.append(('AB',AdaBoostRegressor()))
ensembles.append(('GB',GradientBoostingRegressor()))
ensembles.append(('RF',RandomForestRegressor()))
ensembles.append(('ET',ExtraTreesRegressor()))
results_ensemble=[]
names_ensemble=[ii for ii,_ in ensembles]
for en_name,en_model in ensembles:
    kfold=KFold(n_splits=n_folds,random_state=seed,shuffle=True)
    en_cv_results=cross_val_score(en_model,train_X,train_y,cv=kfold,scoring=scoring_metric)
    results_ensemble.append(en_cv_results)
    print('{}: {:.4f} ({:.4f})'.format(en_name,en_cv_results.mean(),en_cv_results.std()))
plt.figure(2)
plt.boxplot(results_ensemble,labels=names_ensemble)
#%% Ensembles Tunning
#GB
kfold=KFold(n_splits=n_folds,random_state=seed,shuffle=True)
gb_model=GradientBoostingRegressor(random_state=seed)
n_est=np.arange(100,150,10)
gb_grid_params={'n_estimators':n_est}
gb_grid=GridSearchCV(estimator=gb_model,param_grid=gb_grid_params,scoring=scoring_metric,cv=kfold)
gb_grid_result=gb_grid.fit(train_X,train_y)
print('Best value: {} with {}'.format(gb_grid_result.best_score_,gb_grid_result.best_params_))
gb_grid_means=gb_grid_result.cv_results_['mean_test_score']
gb_grid_std=gb_grid_result.cv_results_['std_test_score']
gb_grid_params=gb_grid_result.cv_results_['params']
for ii in range(0,gb_grid_means.size):
    print('{} ({}) with {}'.format(gb_grid_means[ii],gb_grid_std[ii],gb_grid_params[ii]))
#%% Finalize model
final_model=GradientBoostingRegressor(n_estimators=120,random_state=seed)
final_model.fit(train_X,train_y)
predictions=final_model.predict(val_X)
print(mean_squared_error(val_y,predictions))







