# Tank mixes

## Background

When farmers put **multiple PPPs in the same spray tank**, this is called a *Tank mix*. Tank mixes allow farmers to reduce the ressorce needs for pest control (time, fuel), to increase pest control efficacy, or for pest resistance management. 
As a consequence, the products in a tank mix are **applied at the same field (space), at the same time, using the same technology and risk mitigation**. This can cause different environmental effects than a more variable product use. In order to reflect this PPP use pattern (eg, in pesticide risk assessment) xCP allows to define *Tank mixes*.  

## Parameterisation

xCP has an entity `Tank`. Multiple products can be defined in one tank to ensure that they will be applied on the same date and with the same values for `InCropBuffer` and `InFieldMargin`. Additionally, if the `ApplicationRates` are defined as probability distributions, the sampling of all `ApplicationRates` will occur with the same parameters.

!!! note  
    The number of `Products` in a `Tank` and the number of `ApplicationRates` must be the same; however, no warnings will appear if the numbers are not equal. The first `ApplicationRate` applies to the first product in the `Tank`, the second `ApplicationRate` applies to the second product in the `Tank`, etc.  
    Multiple product names must be separated with a '|' character.


``` xml
<?xml version="1.0" encoding="UTF-8"?>
<PPMCalendar xmlns="urn:xCropProtectionLandscapeScenarioParametrization">
    <TemporalValidity scales="time/simulation"> always </TemporalValidity>
    <TargetCrops type="list[int]" scales="global"> 10 </TargetCrops>
    <Indications>
        <Indication type="xCropProtection.ChoiceDistribution" scales="time/year, space/base_geometry">
            <ApplicationSequence probability="1">
                <Application>
                    <Tank>
                        <Products type="list[str]" scales="other/products">
                            Product 1|Product 2
                        </Products>
                        <ApplicationRates scales="other/products">
                            <ApplicationRate type="float" unit="g/ha" scales="global">
                                100
                            </ApplicationRate>
                            <ApplicationRate type="float" unit="g/ha" scales="global">
                                150
                            </ApplicationRate>
                        </ApplicationRates>
                    </Tank>
                    <ApplicationWindow type="xCropProtection.MonthDaySpan" scales="global">
                        05-01 to 05-10
                    </ApplicationWindow>
                    <Technology scales="global">Technology</Technology>
                    <InCropBuffer type="float" unit="m" scales="global">0</InCropBuffer>
                    <InFieldMargin type="float" unit="m" scales="global">0</InFieldMargin>
                </Application>
            </ApplicationSequence>
        </Indication>
    </Indications>
</PPMCalendar>
```

### Explanation

In this example, Product 1 and Product 2 have been added to one `Tank`. Each year of the simulation, they will both be applied on the same day between May 1st and May 10th (a random day will be selected each year with each day being equally likely). Product 1 will receive an application rate of 100 g/ha and Product 2 will receive an application rate of 150 g/ha. Values for `Technology`, `InCropBuffer`, and `InFieldMargin` will apply to both product applications.

For explanations of each element, see [Simple Scenario](simple-scenario.md).

### Illustration

<img src="../img/tank-mixes.PNG" alt="xCP parameterisation entities and their relationship" width="700"/>

See also ['Indications'](../reference/glossary.md#indication) for the full picture of xCP entities and their relationship.
