## Table of Contents
* [About the project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)


## About the project
A schematic scenario consisting of a field and an adjacent off-field habitat.
This is an automatically generated documentation based on the available scenario metadata. The current version of this 
document is from 2021-12-08.

### Built with
The scenario can be used in the following Landscape Models:
* xOffFieldSoilRisk version 1.2.7 and higher


## Getting Started
### Prerequisites
Make sure you use the latest version of the Landscape Model.

### Installation
Copy the complete scenario folder unaltered into the `scenario` subdirectory of your model. Reference the scenario
from the model parameterization. For details how to reference the scenario from the user parameterization, see the 
`README` of the model.


## Usage
The scenario adds the following macros to the Landscape Model:
* `:weather_mars-97100` (version 1.3.5)
* `:LandscapeScenario` (version 1.0)
* `:VfsMod_lookup_table` (version 1)

### Roadmap
The scenario is final and not further developed. It will be, however, updated to reflect new requirements by the 
Landscape Model core and individual Landscape Model variants.


## Contributing
Contributions are welcome. Please contact the authors (see [Contact](#contact)) and see the `CONTRIBUTING` document.


## License
Distributed under the CC0 License. See `LICENSE` for more information.


## Contact
* Thorsten Schad - thorsten.schad@bayer.com
* Sascha Bub - sascha.bub.ext@bayer.com


## Acknowledgements
* Joachim Kleinmann and Magnus Wang for the VfsMod lookup table
* MARS 25 km x 25 km gridded weather data for MARS grid cell 97100
