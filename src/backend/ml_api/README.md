
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

Run the app:

```
export FLASK_APP=app.py
flask run
```

Run tests:

```
pytest
```