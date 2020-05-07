# Some unit tests

print("Test 1")
df_in = pd.DataFrame(
    {"T_na": [np.nan,np.nan,10,np.nan,np.nan,50],
     "C": [1,1,2,3,20,40]
    })
df_in["T_inter"] = interpolate_by_translation(df_in.T_na, df_in.C)
print(df_in)
print("C/T", (df_in.C.diff() / df_in.T_inter.diff()).tolist())


print("")
print("Test 2")
df_in = pd.DataFrame(
    {"T_na": [10,np.nan,np.nan,50],
     "C": [2,3,20,40]
    })
df_in["T_inter"] = interpolate_by_translation(df_in.T_na, df_in.C)
print(df_in)
print("C/T", (df_in.C.diff() / df_in.T_inter.diff()).tolist())


print("")
print("Test 2.5")
df_in = pd.DataFrame(
    {"T_na": [100e3,np.nan,np.nan,500e3],
     "C": [2e3,3e3,20e3,40e3]
    })
df_in["T_inter"] = interpolate_by_translation(df_in.T_na, df_in.C)
print(df_in)
#df_in.C.plot(); plt.show()
#df_in.T_inter.plot(); plt.show()
print("C/T", (df_in.C.diff() / df_in.T_inter.diff()).tolist())





print("")
print("Test 3")
df_in = pd.DataFrame(
    {"T_na": [np.nan,np.nan,50],
     "C": [3,20,40]
    })
df_in["T_inter"] = interpolate_by_translation(df_in.T_na, df_in.C)
print(df_in)



print("")
print("Test 4.5")
df_in = pd.DataFrame(
    {"T_na": [10,np.nan,10,np.nan,np.nan,80],
     "C": [2,3,20,30,40,50]
    })
try:
    df_in["T_inter"] = interpolate_by_translation(df_in.T_na, df_in.C)
    print(df_in)
    assert(False)
except InterpolationError as e:
    print(str(e))
    print(df_in)
    assert(True)


print("")
print("Test 5")
df_in = pd.DataFrame(
    {"T_na": [10, np.nan, np.nan, 10],
     "C": [2,3,20,40]
    })
df_in["T_inter"] = interpolate_by_translation(df_in.T_na, df_in.C)
print(df_in)
# Should return [10,10,10,10]

print("")
print("Test 5.5")
df_in = pd.DataFrame(
    {"T_na": [6422, np.nan, np.nan,np.nan, 8090],
     "C": [1176,1279,1351,1463,1531]
    })
df_in["T_inter"] = interpolate_by_translation(df_in.T_na, df_in.C)
print(df_in)

print("")
print("Test 6")
df_in = pd.DataFrame(
    {"T_na": [10, np.nan, np.nan, 5],
     "C": [2,3,20,40]
    })
try:
    # Should give an exception since the template is increasing whereas the na-vec is decreasing
    df_in["T_inter"] = interpolate_by_translation(df_in.T_na, df_in.C)
    print(df_in)
    assert(False)
except InterpolationError as e:
    print(str(e))
    print(df_in)
    assert(True)


#########################


# tests
print("test m1")
df_in = pd.DataFrame({"vec_with_na": [np.nan, 5,np.nan,np.nan,10,np.nan,np.nan,50, np.nan],
                      "vec_template": [0, 1,1,1,2,3,20,40, 40]
                     })

vec_inter = interpolate_by_translation_multigap(df_in.vec_with_na, df_in.vec_template)
df_in["inter"] = vec_inter
print('result')


df_in




# tests
print("test m2")
df_in = pd.DataFrame({"vec_with_na": [np.nan, np.nan, 5, np.nan,np.nan,10,np.nan,np.nan,50, np.nan, np.nan],
                      "vec_template": [1,1,1,1,1,2,3,20,40,50,60]
                     })

vec_inter = interpolate_by_translation_multigap(df_in.vec_with_na, df_in.vec_template)
df_in["inter"] = vec_inter
print('result')


df_in
