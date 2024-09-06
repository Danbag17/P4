# P4 Lab

## Introduction

Welcome to the ANET P4 Lab!
In this repository you can find information about your upcoming assignments.

We provide you with a [base code for starting your work](./base_code).

## Assignments

For your assignments you will need to write functionalities into the P4 base code that we provide you.
The description of each assignment is in it's respective folder.

1. Assignment 1: Introduction and Language Basics
    * [Basic Forwarding](./assignments/basic/README.md)
    * [Basic Tunneling](./assignments/basic_tunnel/README.md)

2. Assignment 2: P4Runtime and the Control Plane
    * [P4Runtime](./assignments/p4runtime/README.md)

3. Assignment 3: Firewall
    * [Firewall](./assignments/firewall/README.md)

4. Assignment 4: Load Balance
    * [Load Balance ](./assignments/load_balance/README.md)
    * [Controlled Load Balance](./assignments/controlled_load_balance/README.md)

## Resources
This repo contains:
* slides from the introductory lecture (`P4_Lab_Slides_2024.pdf`)
* alternative slides from [p4.org](https://p4.org/) (`P4_tutorial.pdf`)
* a P4 Cheat Sheet containing various examples that you can use (`p4-cheat-sheet.pdf`)

All excercises in this repository use the v1model architecture, the documentation for which is available at:
1. The BMv2 Simple Switch target document accessible [here](https://github.com/p4lang/behavioral-model/blob/master/docs/simple_switch.md) talks mainly about the v1model architecture.
2. The include file `v1model.p4` has extensive comments and can be accessed [here](https://github.com/p4lang/p4c/blob/master/p4include/v1model.p4).

If you use code from any of these places, or from other places on the internet, please indicate so with a comment.

## Obtaining required software

You can find the VM on the Canvas Files page: https://canvas.utwente.nl/courses/13594/files

Use the VM as follows:

1. Make sure you have [VirtualBox](https://www.virtualbox.org/) installed.
2. Download the VM from the link.
3. Within VirtualBox: File>Import Appliance
4. Follow the steps
5. This repository is already cloned in the VM under `~/p4labs/`
6. Please run `git pull` inside of the repository to obtain the latest version
7. To get your code onto the VM you can: 
    * Write the code on the VM. 
    * Write the code on your own computer and set up a VirtualBox's shared folder to 
      move the code to the VM
    * Write the code on your own computer and copy it using `scp` over an ssh connection.
      The virtual machine should be listening for ssh connections on `localhost:2222`
8. Use proper git practices and commit your code often so that you can pull any further updates of the exercises

The account is `p4` and the password is `p4`.
