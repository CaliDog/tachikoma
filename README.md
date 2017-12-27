<p align="center">
    <img align="center" src="https://user-images.githubusercontent.com/1072598/34377019-e1f96e5c-eaa3-11e7-9778-4550b4c7ddc5.png">
    <p align="center">Security robots so smart it's concerning.</p>
    <p align="center"><a href="https://travis-ci.org/CaliDog/tachikoma"><img src="https://travis-ci.org/CaliDog/tachikoma.svg?branch=master"></a></p>
</p>


## What?

Tachikoma is the alerting and analysis pipeline we've always wanted, but could never seem to find. It's inspired by projects like [Security Monkey](https://github.com/netflix/security_monkey), but attempts to fix what we feel are a number of shortcomings in other platforms.

Tachikoma operates on the concept of a 3-phase **pipeline**, which provides a nice separation of concerns and decouples your logic for retrieving security-relevant data, processing found results, and emitting alerts to 3rd party services (like email or Slack). This makes for much easier testing and readability, while providing good flexibility to analyze and alert on almost anything without going crazy.

Right now it's designed to run in a batch processing mode, so you'd run your Tachikoma pipeline at some fixed interval (like once an hour). Eventually we're going to support real-time pipelines, so you can ingest data from live data sources (like websockets) and use that for triggering alerts as things happen. 

## Design

The general workflow of Tachikoma breaks down into 3 major components, [generators](#generators), [analyzers](#analyzers), and [emitters](#emitters). 

<p align="center">
    <img align="center" src="https://user-images.githubusercontent.com/1072598/31879375-1d6543e8-b792-11e7-8cab-fcce32ab1957.png">
</p>

It's worth noting there **is** some extra processing happening behind the scenes (in the form of a [differs](#differs), [routers](#routers), and a [persistence](#persistence) mechanism), but usually you don't have to concern yourself with it, and you can focus mostly ingesting data, processing it, alerting on it, and moving on with your life.

## Components 

### Generators 

A generator's job is simple - it just generates data. The data can come from anywhere, but the idea is that it should generate **the same** data as long as nothing has changed in whatever data source you want to monitor. A good example of this concept is a generator tasked with watching the slack users for a given organization - the generator generating the list of users will be the exact same every time until a new user is added, or a user is removed. 

Generators can be either coroutines (decorated with `@asyncio.coroutine` or prefixed with the `async` keyword) or regular functions. **If a regular function is used, it will be executed concurrently in a threadpool, so make sure your generators are thread safe!** 

### Differ

The differ sits between the [generators](#generators) and the [router](#router) responsible for dispatching generator results to the [analyzers](#analyzers). It integrates with the [persistence](#persistence) mechanism to get the previous run's generator results, then diffs that data with the current generator results. 

This is an extremely handy thing to have done generically and behind the scenes as it makes writing the logic for the [analyzers](#analyzers) quite easy. For example, if you were monitoring your AWS IAM users for any account additions, it'd be a simple matter of interrogating the diff information passed into your analyzer and emitting based only on that. 

### Persistence

The persistence layer is meant to be a very simple interface with purpose-built functions abstracting away the implementation of *how* the results are stored, and instead focuses on more to-the-point storage and retrieval. 

There are a number of persistence mechanisms already included with Tachikoma, but it's trivial to implement your own and back Tachikoma with whatever storage medium you want!

### Router

The routing layer is used in two places - to route generated data to the [analyzers](#analyzers), and to route analyzer results to [emitters](#emitters). This routing layer is based on a very simple namespacing concept, so while [generators](#generators) have specific names (`aws.iam`, `slack.users`, etc), [analyzers](#analyzers) and [emitters](#emitters) are associated with namespaces. 

For example, when setting up the pipeline you may have a generator named `aws.iam`, and an analyzer listening in the `aws.*` namespace. The analyzer would receive data from any generator prefixed with the `aws` key, so it would receive the `aws.ian` results for analysis. The same idea goes for [emitters](#emitters), and the [emitter](#emitters) namespaces and analyzer namespaces are decoupled, so you can do cool things like have one analyzer for all `aws` services, but have specific [emitters](#emitters) for specific services. 

### Analyzers

Analyzers hold true to their namesake and analyze results coming in from the [generator](#generators) layer (after being diffed by the [diffing engine](#differ)), and receive 4 basic things - the generator's previous results, the generator's current results, a diffing data structure that holds the differences in the results, and a reference to the global shared state. 

Each analyzer is responsible for analyzing their result and [emitting](#emitters) a generic message (with a title, description, and optional extra metadata), which will then be used by the emitting layer to send properly formatted data to each service that's registered for that namespace.

### Emitters

Emitters are the final stop in the pipeline lifecycle, and are responsible for interacting with external services to do things like publish results to an SNS topic, send emails, or trigger a GET request to a specific service. 


## Current Development Status

At Cali Dog we put out OSS projects in a 4-phase release cycle:

* `UNSTABLE` projects are currently being developed in the open,  and probably aren't finished quite yet, so don't expect anything to work or be documented. 
* `ALPHA` projects are ready for testing, though expect bugs and breakage.
* `BETA` projects make some guarantees to stability and api immutability, but be sure to test thoroughly before putting things in production.
* `STABLE` projects are ready for general consumption and use in a production environment.

<p align="center">
    <img align="center" src="https://user-images.githubusercontent.com/1072598/31913475-08f3d162-b7fc-11e7-9cd1-1cd31c055de7.gif">
</p>

The project is currently in the **ALPHA** phase, so it's getting there, but expect some breakage and minimal integrations!
