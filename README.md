<p align="center">
    <img align="center" src="https://user-images.githubusercontent.com/1072598/31910286-d9363686-b7f1-11e7-84b0-852a56e6c085.png">
    <p align="center">Security robots so smart it's concerning.</p>
</p>


## What?

Tachikoma is the alerting and analysis pipeline I've always wanted, but could never seem to find.

Highly concurrent in nature, it runs work in 3 distinct cycles to set up an extremely simple input -> process -> output pipeline. 


## Design

The general workflow of Tachikoma breaks down into 3 major components, [generators](#generators), [analyzers](#analyzers), and [emitters](#emitters). 

There is some extra processing happening behind the scenes (in the form of a [differs](#differs), [routers](#routers), and the [persistence](#persistence) mechanism), but usually you don't have to concern yourself with it, and you can focus mostly on the three major bits which lets you think of the whole pipeline as a basic Input -> Process -> Output sort of chain. 

<p align="center">
    <img align="center" src="https://user-images.githubusercontent.com/1072598/31879375-1d6543e8-b792-11e7-8cab-fcce32ab1957.png">
</p>


## Components 

### Generators 

A generator's job is simple - it just generates data. The data can come from anywhere, but the idea is that it should generate **the same** data as long as nothing has changed in whatever you want to monitor. A good example of this idea is a list of Slack users for a given organization - the generator generating the list of slack users will be the exact same every time until a new user is added, or a user is removed. 

Generators can be either coroutines (decorated with `@asyncio.coroutine` or prefixed with the `async` keyword) or regular functions. If a regular function is used, it will be executed concurrently in a threadpool, so make sure your generators are thread safe!

### Analyzer 

Analyzers hold true to their namesake and analyze results coming in from the generator layer (after being diffed by the diffing engine), and receive 4 basic things - the generator's previous results, the generator's current results, a diffing data structure that holds the differences in the results, and a reference to the global shared state. 

Each analyzer is responsible for analyzing their result and emitting a generic message (with a title and a long description, with optional metadata), which will then be used by the emitting layer to send properly formatted alerts to each service that's registered in the namespace.

### Emitter 

Emitters are the final stop in the pipeline lifecycle, and are responsible for interacting with external services to do things like publish results to an SNS topic, send emails, or trigger a GET request to a specific service. 

### Differ

The differ sits between the generators and the router responsible for dispatching generator results to the analyzers. It integrates with the persistence mechanism to get the previous run's generator results, then diffs that data with the current generator results. 

This is an extremely handy thing to have done generically and behind the scenes as it makes writing the logic for the analyzers quite easy. For example, if you were monitoring your AWS IAM users for any account additions, it'd be a simple matter of interrogating the diff information passed into your analyzer and emitting based only on that. 

### Persistence

The persistence layer is meant to be a very simple interface with purpose-built functions abstracting away the implementation of *how* the results are stored, and instead focuses on more to-the-point storage and retrieval. 

There are a number of persistence mechanisms already included with Tachikoma, but it's trivial to implement your own and back Tachikoma with whatever storage medium you want!

### Router

The routing layer is used in two places - to route generated data to the analyzers, and to route analyzer results to emitters. This routing layer is based on a very simple namespacing concept, so while generators have specific names (`aws.iam`, `slack.users`, etc), analyzers and emitters are associated with namespaces. 

For example, when setting up the pipeline you may have a generator named `aws.iam`, and an analyzer listening in the `aws.*` namespace. The analyzer would receive data from any generator prefixed with the `aws` key, so it would recieve the `aws.ian` results for analysis. The same idea goes for emitters, and the emitter namespaces and analyzer namespaces are decoupled, so you can do cool things like have one analyzer for all `aws` services, but have specific emitters for specific services. 

## Current Development Status

At Cali Dog we put out OSS projects in a 4-phase release cycle:

* `UNSTABLE` projects are currently being developed in the open,  and probably aren't finished quite yet, so don't expect anything to work or be documented. 
* `ALPHA` projects are ready for testing, though expect bugs and breakage.
* `BETA` projects make some guarantees to stability and api immutability, but be sure to test thoroughly before putting things in production.
* `RELEASED` projects are ready for general consumption and use in a production environment.

**The project is currently in the `UNSTABLE` phase, so it's not quite ready for consumption, but we're getting there!**

![](https://user-images.githubusercontent.com/1072598/31913475-08f3d162-b7fc-11e7-9cd1-1cd31c055de7.gif)

## Project Roadmap

- [x] Generator Layer
- [x] Diffing Layer
- [x] Persistence Layer
- [ ] Analyzer layer
- [ ] Emitter layer
- [ ] Test coverage
