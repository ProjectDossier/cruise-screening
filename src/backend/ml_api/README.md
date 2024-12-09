
Create env for prompt_api:

```
conda create -n cruise_ml_api python=3.8.15
```

Activate env:

```
conda activate cruise_ml_api
```

Install requirements:

```
pip install -r requirements.txt
conda install pytorch torchvision torchaudio pytorch-cuda=11.6 -c pytorch -c nvidia
conda install conda-forge::fasttext
```

Run the app from the *ml_api* directory:

```
uvicorn app:app
```

API will be available at [127.0.0.1:8000](http://127.0.0.1:8000)

Swagger UI will be available at [127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Run tests:

```
pytest
```