<h1 align="center">
xCropProtection
</h1>

xCropProtection is a spatiotemporally explicit landscape model component for simulating applications of plant protection products on fields within a landscape.

[CropProtection component's README](https://github.com/xlandscape/CropProtection-Component/blob/main/README.md)

[Landscape model core's README](https://github.com/xlandscape/LandscapeModel-Core)

## Table of Contents
* [About](#about)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
  * [Scenarios](#scenarios)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)

## About
xCropProtection is spatiotemporally explicit component for simulating plant protection product (PPP) applications in a landscape which integrates with a larger spatiotemporal landscape model (xLandscape). This component simulates applications at a field scale given PPP application information including target crops, spatial landscape information, and temporal constraints. Multiple different PPPs can be applied to one or more crop types in a landscape, with application details such as application rate, application date, and mitigation measures defined for each application. Typical PPP spray sequences as recommended by plant protection services can be parameterized incorporating market share of individual products.

The development of the xCropProtection component is intended to support the work on key topics of the future of pesticide risk assessment and risk management, as well as overarching goals of sustainable and regenerative agriculture which require improved operational instruments.

### Built with
* Landscape Model core version 1.17.0
* CropProtection component version 1.18.0
* xCropProtection version 1.2

## Getting Started
The component can be used in any Landscape Model based on core version 1.17.0 or newer. See the Landscape Model core's [`README`](https://github.com/xlandscape/LandscapeModel-Core) for general tips on how to add a component to a Landscape Model.

### Prerequisites
A model developer that wants to add the `xCropProtection` component to a Landscape Model needs to set up the general structure for a Landscape Model first. See the Landscape Model core's [`README`](https://github.com/xlandscape/LandscapeModel-Core) for details on how to do so.

[Git](https://git-scm.com/) must be installed on your computer in order to clone this repository.

### Installation
1. Clone this repository
```
git clone https://github.com/xlandscape/xCropProtectionDemo
```
2. To run the Jupyter notebooks, download Python and install it according to the instructions on their [website](https://www.python.org/downloads/). The notebooks were developed and tested with Python version [3.12.2](https://www.python.org/downloads/release/python-3122/).
3. To install required packages, use
```
pip install -r /path/to/requirements.txt
```
requirements.txt is located in the analysis folder of xCropProtection.

## Usage
To run xCropProtection, drag one of the template.xrun files onto *__start_\_.bat*. These XRUN files contain information about which files will be used as input to xCropProtection. They can be viewed and edited with a text editor such as Notepad. xCropProtection version 1.2 includes the following templates:

* **template.xrun**: Intended to be used to test if the installation of xCropProtection was successful. Uses the demo scenario and PPM Calendars located in *CropProtection\PPMCalendars\Demo-calendars*.
* **template-active-substance-demo.xrun**: Demonstrates how to parameterize xCropProtection using active substances. Uses the demo scenario and PPM Calendars located in *CropProtection\PPMCalendars\Demo-calendars*.
* **template-rummen.xrun**: Runs xCropProtection using the Rummen scenario and a PPM calendar of ficticious product applications to apples. The PPM Calendar used and variations on this calendar are located in *CropProtection\PPMCalendars\Rummen*.
* **template-simple-parser.xrun**: Runs xCropProtection using the Excel user interface located in the *CropProtection* folder.

For information about parameterizing xCropProtection, see the CropProtection component's [`README`](https://github.com/xlandscape/CropProtection-Component/blob/main/README.md). Also, see the Templates section of the documentation for examples and information on how to build your own PPM Calendars.

### Scenarios

xCropProtection version 1.2 includes 2 landscape scenarios:

* **Demo-scenario**: A scenario of 1,000 fields, each assigned one of two landcover types. This scenario is intended to be used to gain familiarity with xCropProtection by providing a small scenario to use for quick simulations. To explore this scenario further, open the QGIS project located in the *scenario\Demo-scenario\Documentation* folder.
* **Rummen**: A scenario representing apple fields in a catchment near Rummen, Belgium. To explore this scenario further, open the QGIS project located in the *scenario\Rummen\Documentation* folder.

## Contributing
Contributions are welcome. Please contact the authors (see [Contact](#contact)).

## Release Notes

### 1.2

Reduced the run time of the CropProtection component.

## License
Distributed under the CC0 License. See `LICENSE` for more information.

## Contact
Thorsten Schad - thorsten.schad@bayer.com  
Sascha Bub - sascha.bub@gmx.de  
Petrus Salminen - petrus.salminen@wsc-regexperts.com  