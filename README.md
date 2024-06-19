# Zone Transfer Tester

This Python script is designed to test if a domain is vulnerable to a DNS zone transfer attack. DNS zone transfer is a method used by attackers to obtain all DNS records for a domain, which can potentially expose sensitive information about the domain's infrastructure.

## Requirements

- Python 3.x
- `dnspython` library

## Installation

1. Clone this repository to your local machine:

    ```bash
    git clone https://github.com/hernandocastelli/zone-transfer.git
    ```

2. Navigate to the project directory:

    ```bash
    cd zone-transfer
    ```

3. Install the required Python dependencies:

    ```bash
    pip install dnspython
    ```

## Usage

Run the script with the domain name you want to test as the argument:

```bash
python zonetransfer.py example.com
```
Replace example.com with the domain you want to test.

## Output

The script can generate a CSV file for ingest into another tool in your recognition workflow or generate an HTML file and plot the information with [Cytoscape](https://github.com/cytoscape/cytoscape.js) as a graph.

![Cytoscape](https://github.com/hernandocastelli/zone-transfer/assets/150078766/a3e826f1-2833-4746-a22a-ea158accaef6)

## License

This project is licensed under the MIT License.

