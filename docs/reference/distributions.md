# Distributions

## Intro
Being an [xLandscape](../xLandscape/xLandscape-intro.md) component, xCP basically works *explicit*, ie, explicitely operates on spatial (eg, fields, region), temporal (eg, day, week, month, season, year) and entities' units (eg, tank, application, indication). However, when simulating real-world landscape-scale phenomenons, eg, for pesticide environmental risk assessment purposes, typically some real-world conditions and processes are not known in detail (down to a number), yet, there is data and/ or knowledge on their general behaviour and ranges. For example, the spatial occurrence and bounderies of fields and species' habitats, together with the fields' historic land use are known (from data bases or remote sensing) with sufficient precision, whereas only reasonable assumptions can be made on the exact land use for next year. For the use of PPPs survey and market data might be available but not their exact use (on specific fields at specific rates) and likewise for a dominating wind direction at a specific day distributions might be available.

This list of vaguely known information for landscape-scale modelling can go on and on. Therefore, [xLandscape](../xLandscape/xLandscape-intro.md) combines the operation of explicit dimensions, units and data with the operation of parameters' *variability* (and *uncertainty*). In an *XLandscape* model run, defined *variability* of natural and agronomic phenomenons is sampled at defined units, and so the space of possible conditions of the modelled systems is *screened* (eg, environmental, land use, pesticide use, etc.).   

Correspondingly, some elements of xCropProtection can be parameterized with probability distributions. When a probability distribution is defined, the distribution is sampled every time step an application occurs (daily). The following are elements which support probability distributions:

- `Indications`
- `Indication`
- `ApplicationRate`
- `InCropBuffer`
- `InFieldMargin`
- `MinimumAppliedArea`

Distribution types currently not available in xCP can be implemented on demand.
<br>

[Illustration of distributions](https://2.bp.blogspot.com/-SpjgitfNMb0/TteevRR_Y2I/AAAAAAAAAFQ/IZgd32z2AI8/s1600/distributions.png)
:  

<img src="../img/distributions.png" alt="Distributions Illustration" width="1000"/>



## Uniform distribution

This defines a numeric distribution with an arbitrary outcome between *a* and *b* where each outcome is equally likely. *a* and *b* are the minimum and maximum values, respectively. The parameters of a uniform distribution are defined with the following steps:

- Define the element's type as "xCropProtection.UniformDistribution"
- Add a child element `Lower`, which defines the minimum value of the distribution
    - type="float"
    - scales="global"
- Add a child element `Upper`, which defines the maximum value of the distribution
    - type="float"
    - scales="global"

Example:

``` xml
<ApplicationRate type="xCropProtection.UniformDistribution" unit="g/ha" scales="time/year, space/base_geometry">
    <Lower type="float" scales="global">50</Lower>
    <Upper type="float" scales="global">75</Upper> 
</ApplicationRate>
```

Every time an application occurs, xCropProtection will choose a value for `ApplicationRate` between 50 and 75 following the rules of uniform distributions.

Elements which may use this distribution are:

- `ApplicationRate`
- `InCropBuffer`
- `InFieldMargin`
- `MinimumAppliedArea`

## Discrete uniform distribution

This defines a numeric distribution with an arbitrary outcome between *a* and *b* where a finite number of outcomes are equally likely. *a* and *b* are the minimum and maximum values, respectively. The parameters of a discrete uniform distribution are defined with the following steps:

- Define the element's type as "xCropProtection.DiscreteUniformDistribution"
- Add a child element `Lower`, which defines the minimum value of the distribution
    - type="float"
    - scales="global"
- Add a child element `Upper`, which defines the maximum value of the distribution
    - type="float"
    - scales="global"

Example:

``` xml
<InCropBuffer type="xCropProtection.DiscreteUniformDistribution" unit="m" scales="time/year, space/base_geometry">
    <Lower type="float" scales="global">0</Lower>
    <Upper type="float" scales="global">10</Upper> 
</InCropBuffer>
```

Every time an application occurs, xCropProtection will choose a value for that application's `InCropBuffer` between 0 and 10 following the rules of discrete uniform distributions. Currently, the sampling methods of uniform distributions and discrete uniform distributions are the same in xCropProtection.

Elements which may use this distribution are:

- `ApplicationRate`
- `InCropBuffer`
- `InFieldMargin`
- `MinimumAppliedArea`

## Normal distribution

This defines a continuous bell-shaped probability distribution of numeric values. It is symmetrical about its mean (*μ*) and most values cluster around the center of the range. The parameters of a normal distribution are defined with the following steps:

- Define the element's type as "xCropProtection.NormalDistribution"
- Add a child element `Mean`, which defines the mean value of the distribution
    - type="float"
    - scales="global"
- Add a child element `SD`, which defines the standard deviation of the distribution
    - type="float"
    - scales="global"

Example:

``` xml
<ApplicationRate type="xCropProtection.NormalDistribution" unit="g/ha" scales="time/year, space/base_geometry">
    <Mean type="float" scales="global">50</Mean>
    <SD type="float" scales="global">4.5</SD> 
</ApplicationRate>
```

Every time an application occurs, xCropProtection will choose a value for `ApplicationRate` following the rules of uniform distributions (with a mean of 50 and a standard deviation of 4.5).

Elements which may use this distribution are:

- `ApplicationRate`
- `InCropBuffer`
- `InFieldMargin`
- `MinimumAppliedArea`

## Choice distribution

This represents a distribution over a set of objects. Each object has an associated probability that determines how likely that object will be selected compared to the other objects in the distribution. All probabilities must sum to 1.0. The parameters of a choice distribution are defined with the following steps:

- Define the element's type as "xCropProtection.ChoiceDistribution"
- Create one or more child elements that represent possible choices
    - probability="*x*" where 0 ≤ *x* ≤  1

Example:

``` xml
<Indication type="xCropProtection.ChoiceDistribution" scales="time/year, space/base_geometry">
    <ApplicationSequence probability="0.4">
        ...
    </ApplicationSequence>
    <ApplicationSequence probability="0.5">
        ...
    </ApplicationSequence>
    <ApplicationSequence probability="0.1">
        ...
    </ApplicationSequence>
```

Elements which may use this distribution are:

- `Indications`
    - Child element: `Indication`
- `Indication`
    - Child element: `ApplicationSequence`