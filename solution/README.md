# Solution to the ratedlabs coding challenge
# Clone the repository
`git clone --recurse-submodules git@github.com:Haypierre/ratedlabs-challenge.git`

# Getting started
```shell
# Install dependencies
pdm sync
# start the database
docker compose up -d -V --wait
# Run the test suite
pdm test
# Run the development server
pdm dev
```

# Visit API documentation
- `http://0.0.0.0:80/docs`

# Usage

- `curl http://0.0.0.0:80/transactions/0x5fde6d5674f9fc8538234ea7d873d226689af08269fdff6c62df4d00d40dc7e1`
- `curl http://0.0.0.0:80/stats`
