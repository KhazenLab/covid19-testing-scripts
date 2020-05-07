
from ..lib.utils import add_context_to_bool_loc
df = pd.DataFrame({
    "A": [1,2,3,4,5,6,1,2,3,4,5,6,4],
    "B": [1,1,1,1,1,1,2,2,2,2,2,2,3]})
df["is_4"] = df.A==4
loc_ctx = add_context_to_bool_loc(df, "B", "is_4", 3)
assert (loc_ctx==[F,F,T,T,T,F,
                  F,F,T,T,T,F,
                  T]).all()

