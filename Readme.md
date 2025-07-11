# TestmoOverview

TestmoOverview is a Python project designed to provide a streamlined interface for interacting with Testmo via both the GUI and API. The project is optimized for Windows environments and automates setup and execution through an easy-to-use batch file.

## Getting Started

### Prerequisites

* Windows OS
* Python needs to be installed. The script was tested against Python3.13.
* Git (for cloning the repository)

### Installation

1. **Clone the Repository**


   Change to your projects directory, open a command prompt and run:

   ```bash
   git clone https://github.com/iljahoffmann/TestmoOverview
   cd TestmoOverview
   ```

2. **Run the Setup Script**

   In the project directory, execute:

   ```bash
   setup.bat
   ```

   This script will:

   * Create a new Python virtual environment
   * Install all required Python packages from `requirements.txt`
   * Prompt you for your Testmo credentials (user name/email and password for GUI login)
   * Ask for your Testmo API token

3. **Run the Application**

   After setup, you will find a new executable file:

   ```
   testmo_overview.exe
   ```

   Simply double-click the executable or run it from the command line to start the application.

## Usage

Once the application is running, follow on-screen instructions. Once a report was created, Excel should be started as the viewer.


## License

(c) 2025 by Yacoub GmbH. All rights reserved.

