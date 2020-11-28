import s3fs
import pandas as pd
BUCKET_NAME = "testernv-cli"


if __name__ == "__main__":

  # ...
  # your data preprocessing...

  s3 = s3fs.S3FileSystem(anon=False)
  df = pd.DataFrame(data={"foo":[0]})
  print(df)

  with s3.open(f"{BUCKET_NAME}/data_bow_limit40000.csv",'w') as f:
      df.to_csv(f)