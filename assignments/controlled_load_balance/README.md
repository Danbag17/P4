# Controlled Load Balancing

In this exercise, you will adapt the previous Load Balancing exercise to let the control plane decide on the division of load over the 2 links. The control plan will decide on this based on the load as measured by the data plane. You will adapt the next-hop table so that it has 100 entries, and have the P4Runtime program modify the amount of entries pointing to  each link depending on the load reported by the switch. For this, the switch will keep a counter for each link that P4Runtime can read.

## Step 0: Copy your Load Balance and Basic solutions

Copy your `load_balance.p4` from the previous Load Balance exercise into this directory. Make sure it is still called `load_balance.p4`. Also copy your `basic.p4` from e.g. the firewall or basic assignment into this directory. 

`s1` will be the load balancing switch, redirecting to either `s2` or `s3`, which will run `basic.p4` to perform the basic IPv4 forwarding. You will not be interacting with `s2` or `s3` from P4Runtime.


## Step 1: Run your (incomplete) code

The code you wrote before should still compile in this slightly different setup.

1. In your shell, run:
   ```bash
   make
   ```
   This will:
   * compile `load_balance.p4`, and
   * start a Mininet instance with three switches (`s1`, `s2`, `s3`) configured
     in a triangle, each connected to one host (`h1`, `h2`, `h3`).
   * The hosts are assigned IPs of `10.0.1.1`, `10.0.2.2`, etc.
   * We use the IP address `10.0.0.1` to indicate traffic that should be
     load balanced between `h2` and `h3`.
   * install the rules from `s2-runtime.json` and `s3-runtime.json`
2. Open another shell in this directory and run the starter code:

   ```bash
   python3 balance_controller.py
   ```
   The starter code will only install the egress rules and nothing else.
3. In the Mininet command prompt, open three terminals
   for `h1`, `h2` and `h3`:
   
   ```bash
   mininet> xterm h1 h2 h3
   ```
4. Each host includes a small Python-based messaging client and
   server.  In `h2` and `h3`'s XTerms, start the servers:
   
   ```bash
   python3 receive.py
   ```
5. In `h1`'s XTerm, send multiple messages from the client. 
   **Note, we are using a new `send_many` command**
   
   ```bash
   python3 send_many.py 10.0.0.1 10
   ```
   This will send 10 messages with random lengths.
6. Type `exit` to leave each XTerm and the Mininet command line.

The message was not received because the ingress tables in `s1` are not populated yet. You will now finish the `balance_controller.py` program to insert and modify entries into `s1`'s ingress tables.

## Step 2: Implement Control for Load Balancing

The `load_balance.p4` program needs to be extended with 2 features:

1. Add 2 counters. In the p4runtime exercise you have learned how to make these. Each counter corresponds to one of the two outgoing links. Each should count the number of bytes (number of packets as in p4runtime is not needed) going over that link.
2. Add a 32-bit parameter to the `set_nhop` action called `link_index` which indicates which link the packet should be sent over. Use this to increment the counter corresponding to this link.

The `balance_controller.py` file contains a skeleton P4Runtime program with key
pieces of logic replaced by `TODO` comments. These should guide your
implementation---replace each `TODO` with logic implementing the
missing piece.

A complete `balance_controller.py` will contain the following components:

1. **TODO** A function that writes the ecmp group values called `writeEcmpGroupValues`
2. **TODO** A function that writes the next hop rules called `writeEcmpNextHopRules`. 
   This function will:
   1. Create a total of `NHOP_TABLE_ENTRIES` (default 100) table entries, divided over the two links according to the provided division in `entry_amounts`
   2. Write the table entries to the switch using the provided `update_type`. 
      This is because we need to specify that we are doing a `MODIFY` operation 
      when changing the table entries instead of inserting them.
3. A function that writes the send frame rules called `writeEgressSendFrameRules`
4. A function that that determines a division of table entries based on the load 
   on the two links called `balanceEntryAmounts`
5. A function that can be used to print the table rules installed on a switch 
   called `readTableRules`
6. A function to print information of an GRPC error (communication protocol)
   called `printGrpcError`
7. A function to obtain the byte count of a counter on a switch called `getByteCounter`
8. **TODO** A function that sets up the connection with the balancing 
   switch and install the initial rules called `setupBalancingSwitch`. You should call 
   the function `writeEcmpNextHopRules` to set the initial entries.
9. The main function that:
   1. Sets up the helper and switch
   2. **TODO** Every 2 seconds reads out the 2 counters and computes the new `entry_amounts`
   3. **TODO** Use the new `entry_amounts` write the new ECMP next hop rules
   4. **TODO** Prints the load counter and `entry_amounts`
10. Some code that parses the command line arguments and does input validation


## Step 3: Run your solution

Follow the instructions from Step 1.  This time you can view the 
load and division of entries in the output of the `balance_controller.py`.
Try a few times with 

Does this algorithm work well? Does it converge or diverge? 

### Troubleshooting

There are several ways that problems might manifest:

1. `load_balance.p4` fails to compile.  In this case, `make` will
report the error emitted from the compiler and stop.

2. `load_balance.p4` compiles but does not support the control plane
rules in the `sX-runtime.json` files that `make` tries to install
using the Python controller.  In this case, `make` will log the
controller output in the `logs` directory. Use the error messages to
fix your `load_balance.p4` implementation.

3. `load_balance.p4` compiles, and the control plane rules are
installed, but the switch does not process packets in the desired way.
The `logs/sX.log` files contain trace messages
describing how each switch processes each packet.  The output is
detailed and can help pinpoint logic errors in your implementation.

#### Cleaning up Mininet

In the latter two cases above, `make` may leave a Mininet instance
running in the background.  Use the following command to clean up
these instances:

```bash
mn -c
```

## Next Steps

Congratulations, you are done with the last exercise! 
Make sure that they are all in working order and include documentation
to sign them off.

## Relevant Documentation

The documentation for P4_16 and P4Runtime is available [here](https://p4.org/specs/)

All excercises in this repository use the v1model architecture, the documentation for which is available at:
1. The BMv2 Simple Switch target document accessible [here](https://github.com/p4lang/behavioral-model/blob/master/docs/simple_switch.md) talks mainly about the v1model architecture.
2. The include file `v1model.p4` has extensive comments and can be accessed [here](https://github.com/p4lang/p4c/blob/master/p4include/v1model.p4).
