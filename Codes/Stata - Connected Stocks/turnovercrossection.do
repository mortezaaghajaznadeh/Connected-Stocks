cls
clear
import delimited "G:\Economics\Finance(Prof.Heidari-Aghajanzadeh)\Data\Connected stocks\turnovercrosssection.csv", encoding(UTF-8) 


cd "D:\Dropbox\Connected Stocks\Connected-Stocks\Final Report"

xtset id year

 
egen double_cluster = group(symbol year)


gen size = log(marketcap)

gen Excess = (cr - cf)/cr


xtile  median = Excess, nq(4)
gen ExcessHigh = 0
replace ExcessHigh = 1 if  median >= 4
drop median
gen ExcessDiff = cr - cfr

gen ExcessDummy = 0
replace ExcessDummy = 1 if ExcessDiff>0



foreach v of varlist size Excess ExcessHigh amihud lowimbalancestd ExcessDiff turnover ExcessDummy {
	gen lag_`v'= l.`v'
	
}


label variable lag_Excess "Excess"
label variable lag_ExcessDummy "ExcessDummy"
label variable lag_ExcessDiff "ExcessDiff"
label variable lag_ExcessHigh "ExcessHigh"
label variable lag_lowimbalancestd "Low Imbalance std"






eststo v0: quietly regress coef_delta_amihud_group lag_Excess i.year, cluster(double_cluster)
estadd loc controll "No" , replace
estadd loc timeEffect "Yes" , replace
eststo v1: quietly regress coef_delta_amihud_group  lag_lowimbalancestd  i.year, cluster(double_cluster)
estadd loc controll "No" , replace
estadd loc timeEffect "Yes" , replace
eststo v2: quietly regress coef_delta_amihud_group  lag_ExcessHigh  i.year, cluster(double_cluster)
estadd loc controll "No" , replace
estadd loc timeEffect "Yes" , replace

eststo v3: quietly regress coef_delta_amihud_group  lag_ExcessDiff  i.year, cluster(double_cluster)
estadd loc controll "No" , replace
estadd loc timeEffect "Yes" , replace

eststo v4: quietly regress coef_delta_amihud_group  lag_ExcessDummy  i.year, cluster(double_cluster)
estadd loc controll "No" , replace
estadd loc timeEffect "Yes" , replace



eststo v01: quietly regress coef_delta_amihud_group lag_Excess  lag_size lag_amihud  i.year, cluster(double_cluster)
estadd loc controll "Yes" , replace
estadd loc timeEffect "Yes" , replace

eststo v11: quietly regress coef_delta_amihud_group  lag_lowimbalancestd lag_size lag_amihud  i.year, cluster(double_cluster)
estadd loc controll "Yes" , replace
estadd loc timeEffect "Yes" , replace


eststo v21: quietly regress coef_delta_amihud_group  lag_ExcessHigh lag_size lag_amihud  i.year, cluster(double_cluster)
estadd loc controll "Yes" , replace
estadd loc timeEffect "Yes" , replace

eststo v31: quietly regress coef_delta_amihud_group  lag_ExcessDiff lag_size lag_amihud  i.year, cluster(double_cluster)
estadd loc controll "Yes" , replace
estadd loc timeEffect "Yes" , replace

eststo v41: quietly regress coef_delta_amihud_group  lag_ExcessDummy lag_size lag_amihud  i.year, cluster(double_cluster)
estadd loc controll "Yes" , replace
estadd loc timeEffect "Yes" , replace


esttab v0 v01  v4 v41 v3 v31 v2 v21  v1 v11  ,keep(lag_Excess lag_lowimbalancestd ) order(lag_Excess lag_ExcessDummy lag_ExcessDiff lag_ExcessHigh lag_lowimbalancestd ) s( N controll timeEffect r2 ,  lab("Observations" "Time FE" "Controls" "$ R^2 $"))   nomtitle label compress  mgroups("Dependent Variable: $ \beta_{Group} $ "   , pattern(1 ) prefix(\multicolumn{@span}{c}{) suffix(}) span erepeat(\cmidrule(lr){@span}) ),using Amihudcrosssection.tex ,replace

 
 /**/

eststo v0: quietly regress coef_deltagroup lag_Excess i.year, cluster(double_cluster)
estadd loc controll "No" , replace
estadd loc timeEffect "Yes" , replace
eststo v1: quietly regress coef_deltagroup  lag_lowimbalancestd  i.year, cluster(double_cluster)
estadd loc controll "No" , replace
estadd loc timeEffect "Yes" , replace
eststo v2: quietly regress coef_deltagroup  lag_ExcessHigh  i.year, cluster(double_cluster)
estadd loc controll "No" , replace
estadd loc timeEffect "Yes" , replace

eststo v3: quietly regress coef_deltagroup  lag_ExcessDiff  i.year, cluster(double_cluster)
estadd loc controll "No" , replace
estadd loc timeEffect "Yes" , replace

eststo v4: quietly regress coef_deltagroup  lag_ExcessDummy i.year, cluster(double_cluster)
estadd loc controll "No" , replace
estadd loc timeEffect "Yes" , replace



eststo v01: quietly regress coef_deltagroup lag_Excess  lag_size lag_turnover  i.year, cluster(double_cluster)
estadd loc controll "Yes" , replace
estadd loc timeEffect "Yes" , replace

eststo v02: quietly regress coef_deltagroup  lag_lowimbalancestd lag_size lag_turnover  i.year, cluster(double_cluster)
estadd loc controll "Yes" , replace
estadd loc timeEffect "Yes" , replace


eststo v03: quietly regress coef_deltagroup  lag_ExcessHigh lag_size lag_turnover  i.year, cluster(double_cluster)
estadd loc controll "Yes" , replace
estadd loc timeEffect "Yes" , replace


eststo v04: quietly regress coef_deltagroup  lag_ExcessDiff lag_size lag_turnover  i.year, cluster(double_cluster)
estadd loc controll "Yes" , replace
estadd loc timeEffect "Yes" , replace

eststo v05: quietly regress coef_deltagroup  lag_ExcessDummy lag_size lag_turnover  i.year, cluster(double_cluster)
estadd loc controll "Yes" , replace
estadd loc timeEffect "Yes" , replace



esttab v0 v01  v4 v41 v3 v31 v2 v21  v1 v11  ,keep(lag_Excess lag_lowimbalancestd ) order(lag_Excess lag_ExcessDummy lag_ExcessDiff lag_ExcessHigh lag_lowimbalancestd ) s( N controll timeEffect r2 ,  lab("Observations" "Time FE" "Controls" "$ R^2 $"))  nomtitle label compress  mgroups("Dependent Variable: $ \beta_{Group} $ "   , pattern(1 ) prefix(\multicolumn{@span}{c}{) suffix(}) span erepeat(\cmidrule(lr){@span}) ),using Turnovercrosssection.tex ,replace