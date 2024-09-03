# Python APIs

![License](https://img.shields.io/github/license/keremsemiz/python-apis)
![Contributors](https://img.shields.io/github/contributors/keremsemiz/python-apis)
![Issues](https://img.shields.io/github/issues/keremsemiz/python-apis)
![Forks](https://img.shields.io/github/forks/keremsemiz/python-apis)
![Stars](https://img.shields.io/github/stars/keremsemiz/python-apis)

A collection of Python scripts that interact with various APIs, showcasing how to integrate third-party services into your Python applications.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

This project contains a set of Python scripts that demonstrate how to interact with various APIs. Each script is focused on a different API, providing examples and best practices for making HTTP requests, handling responses, and processing data.

## Features

- Easy-to-understand examples for multiple APIs.
- Demonstrates both GET and POST requests.
- Includes error handling and logging.
- Configurable via environment variables.

## Installation

To run the scripts in this repository, you will need Python 3.x and the following dependencies:

```bash
pip install -r requirements.txt
```

Clone the repository:

```bash
git clone https://github.com/keremsemiz/python-apis.git
cd python-apis
```

## Usage

Each script in the `Intermediate APIs` and `Basic APIs` folder is designed to be run individually. Below is an example of how to run a script:

```bash
python Intermediate APIS/test123.py
```

You may need to configure your API keys and other settings. These can be set in a `.env` file at the root of the project. Example:

```ini
API_KEY=your_api_key_here
```

## Examples

Here are a few examples of the APIs included:

- **Weather API**: Fetches current weather data for a given location.
- **Stock API**: Retrieves the latest stock market data.
- **Currency Exchange API**: Converts amounts between different currencies.

## Screenshots

<img width="1136" alt="Screenshot 2024-09-03 at 22 31 13" src="https://github.com/user-attachments/assets/4c759067-1373-4a51-b27a-4c3694e81319">

## Contributing

Contributions are welcome! Please fork this repository, create a new branch, and submit a pull request with your changes.

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature-name`)
5. Open a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
