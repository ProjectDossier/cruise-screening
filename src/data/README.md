## Usage


Get the dataset as jsonl:

```bash
$ mkdir -p tmp

$ wget -c -O tmp/dblp.v13.7z https://originalstatic.aminer.cn/misc/dblp.v13.7z

$ 7za x -o"tmp" tmp/dblp.v13.7z

$ python get_AMiner.py -p tmp
```

Filter documents and specific fields from the dataset:

```bash
$ python filter_AMiner.py -p tmp
```




