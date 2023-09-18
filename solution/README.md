# Solution to the ratedlabs coding challenge
# Clone the repository
`git clone --recurse-submodules git@github.com:Haypierre/ratedlabs-challenge.git`

# Start the server
To launch the server, run the following commands:
- `cd solution`
- `pdm install`
- `eval $(pdm venv activate)`
- `docker compose up`
- `export $(cat test.env)`
- `uvicorn src.main:app --host 0.0.0.0 --port 80`

# Visit API documentation
- `http://0.0.0.0:80/docs`

# Usage

- `curl http://0.0.0.0:80/transactions/0x5fde6d5674f9fc8538234ea7d873d226689af08269fdff6c62df4d00d40dc7e1`
- `curl http://0.0.0.0:80/stat`

# Run the tests suite
- `cd solution`
- `eval $(pdm venv activate)`
- `export $(cat test.env)`
- `pytest`
