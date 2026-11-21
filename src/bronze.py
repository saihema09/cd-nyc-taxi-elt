import shutil, sys, pathlib

month = sys.argv[1]  # e.g. 2024-01
src = pathlib.Path(f"data/raw/yellow_tripdata_{month}.parquet")
dst = pathlib.Path(f"data/bronze/yellow/month={month}/trips.parquet")
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(src, dst)
print(f"Bronze written: {dst}")