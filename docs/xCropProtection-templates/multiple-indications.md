# Multiple Indications

## Background
In agricultural practice, an *Indication* basically represents control measures against a certain pest in a crop, eg, to control powdery mildew in vines, brown rot in apple, whitefly in olives, or blackgras in wheat.  
A composition of *Indications* defines a *Crop Protection Calender*, eg, all the *Indications* to control fungy, insects pests and weeds in vines across a growing season. See also [Indications](../reference/glossary.md#indication) in the [Glossary](../reference/glossary.md).

## Parameterisation
A PPMCalendar can have 1 or more `Indication` elements in its list of `Indications`. When xCropProtection runs, all `Indication` elements are executed within which one `ApplicationSequence` from each `Indication` will be chosen. Indications hold one or more `ApplicationSequence` elements which each have a probability associated with them.   
Multiple `Indication` elements should be used when multiple `Products` need to be applied to a field type.  

``` xml
<?xml version="1.0" encoding="UTF-8"?>
<PPMCalendar xmlns="urn:xCropProtectionLandscapeScenarioParametrization">
    <TemporalValidity scales="time/simulation"> always </TemporalValidity>
    <TargetCrops type="list[int]" scales="global"> 10 </TargetCrops>
    <Indications>
        <Indication type="xCropProtection.ChoiceDistribution" scales="time/year, space/base_geometry">
            <ApplicationSequence probability="0.7">
                <Application>
                    <Tank>
                        <Products type="list[str]" scales="other/products">
                            Product 1
                        </Products>
                        <ApplicationRates scales="other/products">
                            <ApplicationRate type="float" unit="g/ha" scales="global">
                                100
                            </ApplicationRate>
                        </ApplicationRates>
                    </Tank>
                    <ApplicationWindow type="xCropProtection.MonthDaySpan" scales="global">
                        06-05 to 06-25
                    </ApplicationWindow>
                    <Technology scales="global">Technology</Technology>
                    <InCropBuffer type="float" unit="m" scales="global">0</InCropBuffer>
                    <InFieldMargin type="float" unit="m" scales="global">0</InFieldMargin>
                </Application>
            </ApplicationSequence>
            <ApplicationSequence probability="0.3">
                <Application>
                    <Tank>
                        <Products type="list[str]" scales="other/products">
                            Product 2
                        </Products>
                        <ApplicationRates scales="other/products">
                            <ApplicationRate type="float" unit="g/ha" scales="global">
                                200
                            </ApplicationRate>
                        </ApplicationRates>
                    </Tank>
                    <ApplicationWindow type="xCropProtection.MonthDaySpan" scales="global">
                        06-05 to 06-25
                    </ApplicationWindow>
                    <Technology scales="global">Technology</Technology>
                    <InCropBuffer type="float" unit="m" scales="global">0</InCropBuffer>
                    <InFieldMargin type="float" unit="m" scales="global">0</InFieldMargin>
                </Application>
            </ApplicationSequence>
        </Indication>
        <Indication type="xCropProtection.ChoiceDistribution" scales="time/year, space/base_geometry">
            <ApplicationSequence probability="0.2">
                <Application>
                    <Tank>
                        <Products type="list[str]" scales="other/products">
                            Product 3
                        </Products>
                        <ApplicationRates scales="other/products">
                            <ApplicationRate type="float" unit="g/ha" scales="global">
                                100
                            </ApplicationRate>
                        </ApplicationRates>
                    </Tank>
                    <ApplicationWindow type="xCropProtection.MonthDaySpan" scales="global">
                        04-01 to 04-15
                    </ApplicationWindow>
                    <Technology scales="global">Technology</Technology>
                    <InCropBuffer type="float" unit="m" scales="global">0</InCropBuffer>
                    <InFieldMargin type="float" unit="m" scales="global">0</InFieldMargin>
                </Application>
            </ApplicationSequence>
            <ApplicationSequence probability="0.8">
                <Application>
                    <Tank>
                        <Products type="list[str]" scales="other/products">
                            Product 4
                        </Products>
                        <ApplicationRates scales="other/products">
                            <ApplicationRate type="float" unit="g/ha" scales="global">
                                200
                            </ApplicationRate>
                        </ApplicationRates>
                    </Tank>
                    <ApplicationWindow type="xCropProtection.MonthDaySpan" scales="global">
                        04-12 to 04-20
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

In this example, a field with LULC type 10 will receive 1 application of either Product 1 or Product 2, **AND** 1 application of either Product 3 or Product 4. Note that the dates of each of these applications are completely independent of each other.

``` xml
<Indications>
    <Indication type="xCropProtection.ChoiceDistribution" scales="time/year, space/base_geometry">
        <ApplicationSequence probability="0.7">
            <Application>
                <Tank>
                    <Products type="list[str]" scales="other/products">
                        Product 1
                    ...
                </Tank>
                ...
            </Application>
        </ApplicationSequence>
        <ApplicationSequence probability="0.3">
            <Application>
                <Tank>
                    <Products type="list[str]" scales="other/products">
                        Product 2
                    </Products>
                    ...
                </Tank>
                ...
            </Application>
        </ApplicationSequence>
    </Indication>
    <Indication type="xCropProtection.ChoiceDistribution" scales="time/year, space/base_geometry">
            <ApplicationSequence probability="0.2">
                <Application>
                    <Tank>
                        <Products type="list[str]" scales="other/products">
                            Product 3
                        </Products>
                        ...
                    </Tank>
                    ...
                </Application>
            </ApplicationSequence>
            <ApplicationSequence probability="0.8">
                <Application>
                    <Tank>
                        <Products type="list[str]" scales="other/products">
                            Product 4
                        </Products>
                        ...
                    </Tank>
                    ...
                </Application>
            </ApplicationSequence>
        </Indication>
</Indications>
```
  
For explanations of each element, see [Simple Scenario](simple-scenario.md).


### Illustration

<img src="../img/Multiple-indications.PNG" alt="xCP parameterisation entities and their relationship" width="600"/>  

See also ['Indications'](../reference/glossary.md#indication) for the full picture of xCP entities and their relationship.
