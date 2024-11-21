# xToxicLoad

xToxicLoad is a Landscape Model that calculates simple toxic load values of pesticides by field and time step (typically by day).  
A *toxic load* represents the multiple of an effect (on a field, at a certain time). It is calculated by deviding the exposure by a defined ecotoxicological endpoint: eg, *ToxicLoad(x,t)* = *PEC(x,t)* / *LD50*. In the example an LD50 is used, however, the ecotox endpoint can be any of interest. A LD50, eg, might represent an oral or contact bee ecotox endpoint.


## Background
At present, intended for demonstration purposes, 

## Installation

To clone the xToxicLoad repository, you must have access to the private repository. Contact Sascha Bub ([sascha.bub@rptu.de](mailto:sascha.bub@rptu.de)) or Thorsten Schad ([thorsten.schad@bayer.com](mailto:thorsten.schad@bayer.com)) for access to the repository. Cloning steps vary based on application.

- [Sourcetree](https://support.atlassian.com/bitbucket-cloud/docs/clone-a-git-repository/)
- [Visual Studio Code](https://learn.microsoft.com/en-us/azure/developer/javascript/how-to/with-visual-studio-code/clone-github-repository?tabs=activity-bar)

The following shows what the folder structure should look like when the cloning process has completed:

``` { .yaml .no-copy }
├── analysis
│   ├── product-and-type.xlsx
│   ├── xCP-movie.ipynb
│   ├── xCP-plot-application-rate-uc4.ipynb
│   ├── xCP-total-loading-uc4.ipynb
│   ├── xCP-write-csv.ipynb
│   ├── xTL-movie-contact-toxicity.ipynb
│   ├── xTL-movie-oral-toxicity.ipynb
│   └── xTL-plot-toxic-load.ipynb
├── chemical
│   ├── Substance and product properties - test1.xlsx
│   ├── Insecticides.xlsx
│   └── product-active-substance.db
├── crop_protection
│   ├── PPMCalendars
│   │   └── Multiple folders of PPM Calendars
│   ├── PPMCalendar-222.xml
│   ├── PPMCalendar-444.xml
│   ├── xCropProtection-Arnsberg.xml
│   ├── xCropProtection-Detmold.xml
│   ├── xCropProtection-Duesseldorf.xml
│   ├── xCropProtection-Koeln.xml
│   ├── xCropProtection-Muenster.xml
│   ├── Technologies.xml
│   └── test1.xml
├── model
│   ├── core
│   │   └── ...
│   ├── variant
│   │   ├── experiment.xml
│   │   ├── mc.xml
│   │   ├── package.xsd
│   │   └── parameters.json
├── run
├── scenario
│   ├── Rummen-xToxicLoad-Test
│   │   ├── geo
│   │   │   ├── (multiple shp files)
│   │   │   └── package.xinfo
│   │   └── scenario.xproject
│   ├── Arnsberg
│   ├── Detmold
│   ├── Duesseldorf
│   ├── Koeln
│   ├── Muenster
├── .gitignore
├── .gitmodules
├── README.md
├── __start__.bat
├── template.xrun
├── Arnsberg.xrun
├── Detmold.xrun
├── Duesseldorf.xrun
├── Koeln.xrun
└── Muenster.xrun
```

## xToxicLoad components

xToxicLoad makes use of multiple other components during a simulation run. 

### Landscape scenario

This component is used to ingest geospatial input and provide geospatial data to the Landscape Model. The parameterization for this component is located in the *package.xinfo* file, where shapefile name and column definitions can be modified.

See [xLandscape](../xLandscape/xLandscape-intro.md) for more details on parameterization and component input/output.

### Product and substance properties

This component is used to read chemical properties located in the substance and product properties table (located in *xToxicLoad/chemical*). User-defined properties and chemical names included in the output of an xToxicLoad simulation.

### xCropProtection

xCropProtection uses the LandscapeScenario component to generate application dates and rates of substances defined in PPM Calendars. PPM Calendars define what products are used during a simulation, with restrictions on what fields, crop types, and dates applications can occur. To introduce variability, probability distribution functions and choices between multiple products can be implemented. The output of xCropProtection is a list of product applications with information about what product was applied and about the application itself.

See the [xCropProtection documentation](https://xlandscape.github.io/xCropProtectionDemoDoc/) for a detailed explanation of how xCropProtection works and example scenarios.

### In field exposure

This component is used to calculate the in-field exposure of substances on a daily basis. It is used as an intermediary step between xCropProtection and xToxicLoad to calcualte PEC values on a daily and field-wise scale. The output of this component is a 3-dimensional array of PEC values.
