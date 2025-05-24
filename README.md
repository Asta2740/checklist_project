# Checklist Project

This project is designed to perform various hardware tests on a computer system, including keyboard, battery, webcam, audio devices, and hard disk performance. Each test is modularized into separate Python files for better organization and maintainability.

## Project Structure

```
checklist_project
├── src
│   ├── keyboard
│   │   ├── __init__.py
│   │   ├── keyboard_test.py
│   │   └── aqua_key_test.py
│   ├── credentials
│   │   ├── __init__.py
│   │   ├── serial_number.py
│   │   ├── brand_version.py
│   │   └── department.py
│   ├── battery
│   │   ├── __init__.py
│   │   ├── battery_status.py
│   │   └── battery_wear_level.py
│   ├── Bluetooth
│   │   ├── __init__.py
│   │   └── bluetooth.py   
│   │   
│   ├── webcam
│   │   ├── __init__.py
│   │   └── webcam_test.py
│   ├── audio
│   │   ├── __init__.py
│   │   └── microphone_test.py ## contains audio and mic tests
│   │   
│   ├── hard_disk
│   │   ├── __init__.py
│   │   ├── disk_benchmark.py
│   │   └── disk_space_check.py
│   
├── __init__.py
├── generate_checklist.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd checklist_project
   ```

2. **Install dependencies**:
   Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

   Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the hardware tests, execute the `generate_checklist.py` file:
```
python ./generate_checklist.py
```

This will initiate the various tests and provide feedback based on the results. and generate an excel sheet with the reported outcome

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.