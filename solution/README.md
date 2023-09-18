# Solution to the ratedlabs coding challenge
# Clone the repository
`git clone --recurse-submodules git@github.com:Haypierre/ratedlabs-challenge.git`

# Launch instructions
To launch the server, run the following commands:
- `cd solution`
- `pdm install`
- `docker compose up`
- `export $(cat test.env)`
- `uvicorn src.main:app --host 0.0.0.0 --port 80`

# Run the tests suite
- `cd solution`
- `pytest`
