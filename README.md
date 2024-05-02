# llms-for-verified-programs
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Repository containing the dataset, algorithms, experiments and results of the thesis "Large Language Models for Verified Programs".

## Getting started

### Set up the Nagini server
This project depends on the Nagini. Follow the instructions [here](https://github.com/marcoeilers/nagini) to set up Nagini. 
> Note: Nagini requires Python 3.8, hence set it up in a separate virtual environment.

Nagini can be run in server mode using this command:
```bash
python3 -m nagini_translation.main a --server
```
However, a code change in `nagini_translation.main` is required so that the server doesn't crash on exceptions [todo: provide link to modified nagini_translation/main.py here].

The server by default listens on `"tcp://localhost:5555"`, which we've used in the client (`DEFAULT_CLIENT_SOCKET`).

### Set up this project
Create a `.env` file at the root level with the following content. `.gitignore` takes care not to commit this file to version control.
```conf
GPT_SECRET_KEY=sk-<your_api_key>
```
Create a virtual environment with Python 3.12 and install dependencies of the project:
```bash
virtualenv l4vp
soruce l4vp/bin/activate
cd <this_directory>
pip install -r requirements.txt
```

Run experiments in one of the jupyter notebook e.g. [final.ipynb](final.ipynb). Make sure the Nagini server is running.

## Dataset
The (root) dataset [dataset/](dataset/), described in Appendix A.1 of the thesis, consists of 50 methods across 3 predicates (list, lseg, tree) verified for memory safety. A config.json file (e.g. [config.json](dataset/list/config.json)) specifies the dataset completely.
It includes: the unverified program, verification error from Nagini, verified program, the system prompt, and the predicate definition / top level declarations for the predicate.
For improved performance on the first run, we cache the verification error from Nagini using the script provided in [scripts.ipynb](scripts.ipynb).

The [data.py](data.py) module serves as an interface for all dataset operations.

## Few-shot prompting
The `run_example` method in [evaluation.py](evaluation.py) implements "Algorithm 1: $\texttt{TryVerify}_{k,n}$: Prompting with errors" from the thesis. The Evaluation class takes the model and dataset as arguments. The `run_example` method is 
implemented against the general Model interface, making it easy to use generically for different models.

### Models
The model interface and the currently supported models are implemented in [model.py](model.py). The supported models
include OpenAI GPT-3.5, GPT-4, CodeLlama models hosted on TogetherAI, and our custom fine-tuned model hosted on
Amazon SageMaker.

### Incremental Verification
The notebook [final.ipynb](final.ipynb) contains an implementation of the "Algorithm 2: Incremental Verification" described in the thesis. 

## Fine-tuning

### Training dataset generation
"Algorithm 3: Training dataset generation" is implemented in [create_dataset.ipynb](create_dataset.ipynb). This relies
on AST analysis of the verified (or master) program which is implemented [ast_util.py](ast_util.py).

### Fine-tuning on Amazon SageMaker
With the dataset generated (as a jsonl file), the notebook [fine_tuning.ipynb](fine_tuning.ipynb) contains the code to fine-tune the model on Amazon SageMaker. The training script to be run inside the container is in [scripts/sagemaker_train.py](scripts/sagemaker_train.py).

### Deploying and evaluating the fine-tuned model
[fine_tuning.ipynb](fine_tuning.ipynb) also contains code to deploy the fine-tuned model (either synchronously using the
Estimator object after training finishes, or using the model artifacts from S3). Once deployed, note the predictor endpoint
name. Then the model can be evaluated using the Evaluation class just like any other (OpenAI / TogetherAI) model. The notebook [eval_finetuned.ipynb](eval_finetuned.ipynb) contains the code and evaluation results of our three fine-tuned models. A custom inference script is required (as we trained using LoRA, need to combine the adapter with the model during initialization) -- this is present in [scripts_inference/inference.py](scripts_inference/inference.py).

### Results / transcripts
The [final/](final/) directory contains transcripts of running evaluation with few-shot prompting, incremental verification (GPT-4) and our fine-tuned models.