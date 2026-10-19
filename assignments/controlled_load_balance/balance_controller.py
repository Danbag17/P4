#!/usr/bin/env python3
import argparse
import os
import sys
import math
from time import sleep

import grpc
from p4.v1 import p4runtime_pb2

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
import p4runtime_lib.helper
from p4runtime_lib.switch import ShutdownAllSwitchConnections

# Amount of entries in the ecmp_nhop table
NHOP_TABLE_ENTRIES=100

# Action parameters for the two possible links to be passed to the set_nhop action
BALANCER_OUTGOING_DESTINATIONS = [
    {
        "port": 2,
        "link_index": 0,
        "nhop_dmac": "08:00:00:00:01:02",
        "nhop_ipv4": "10.0.2.2",
    },
    {
        "port": 3,
        "link_index": 1,
        "nhop_dmac": "08:00:00:00:01:03",
        "nhop_ipv4": "10.0.3.3"
    },    
]

def writeEcmpGroupValues(p4info_helper, sw):
    
    # TODO 
    # 1) Build a valid table entry for the ecmp_group table
    # and install it on the switch. 
    # For the action parameters: ecmp_base should be 1 and
    # ecmp_count should be equal to NHOP_TABLE_ENTRIES
    # If you are unsure how to build a table entry or how to 
    # install it on the switch, have a look at the p4runtime 
    # exercise again
   
    table_entry = p4info_helper.buildTableEntry(
    table_name="MyIngress.ecmp_group",       
    match_fields={
        "hdr.ipv4.dstAddr" : ("10.0.0.1", 32)      
    },
    action_name="MyIngress.set_ecmp_select",    
    action_params={
        "ecmp_base" : 1,
        "ecmp_count" : NHOP_TABLE_ENTRIES          
    })
    sw.WriteTableEntry(table_entry)         


def writeEcmpNextHopRules(p4info_helper, sw, entry_amounts, update_type=p4runtime_lib.helper.P4InfoHelper.UpdateType.INSERT):
    # TODO 
    # 2) Build the table entries for the next_hop table
    # and install them on the switch. 
    #
    # It should install in total NHOP_TABLE_ENTRIES into the table. 
    # These should be divided according to the entry_amounts argument. 
    # This is a tuple of two values, indicating how many entries 
    # should point to each link. An entry_amount of (40, 60) means 
    # that 40 entries should point the first link and 60 should point 
    # to the second.
    #
    # The entries should point to the set_nhop action and can use the
    # parameters from the BALANCER_OUTGOING_DESTINATIONS list. For 
    # link 0 use the first element of this list, for link 1 use the 
    # second.
    #
    # Make sure to pass the update_type argument into each call of 
    # sw.WriteTableEntry as keyword argument. e.g. 
    # sw.WriteTableEntry(table_entry, update_type=update_type)
    for i in range(NHOP_TABLE_ENTRIES):     
        if (i < entry_amounts[0]):
            link = 0
        else:
            link = 1

        table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ecmp_nhop",       
        match_fields={ "meta.ecmp_select": i + 1 },
        action_name="MyIngress.set_nhop",    
        action_params=
            BALANCER_OUTGOING_DESTINATIONS[link]         
        )
        sw.WriteTableEntry(table_entry,update_type=update_type)         


def writeEgressSendFrameRules(p4info_helper, sw):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyEgress.send_frame",
        match_fields={
            "standard_metadata.egress_port": 2
        },
        action_name="MyEgress.rewrite_mac",
        action_params={
            "smac": "00:00:00:01:02:00"
        }
    )
    sw.WriteTableEntry(table_entry)
    
    
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyEgress.send_frame",
        match_fields={
            "standard_metadata.egress_port": 3
        },
        action_name="MyEgress.rewrite_mac",
        action_params={
            "smac": "00:00:00:01:03:00"
        }
    )
    sw.WriteTableEntry(table_entry)
    
    print(f"Installed send frame rules on switch {sw.name}")

def balanceEntryAmounts(load1, load2):
    total = load1 + load2
    if total == 0:
        return (NHOP_TABLE_ENTRIES//2, NHOP_TABLE_ENTRIES//2)
    return (math.floor(NHOP_TABLE_ENTRIES * load2 / total), math.ceil(NHOP_TABLE_ENTRIES * load1 / total))

def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print('\n----- Reading tables rules for %s -----' % sw.name)
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print('%s: ' % table_name, end=' ')
            for m in entry.match:
                print(p4info_helper.get_match_field_name(table_name, m.field_id), end=' ')
                print('%r' % (p4info_helper.get_match_field_value(m),), end=' ')
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print('->', action_name, end=' ')
            for p in action.params:
                print(p4info_helper.get_action_param_name(action_name, p.param_id), end=' ')
                print('%r' % p.value, end=' ')
            print()

def printGrpcError(e):
    print("gRPC Error:", e.details(), end=' ')
    status_code = e.code()
    print("(%s)" % status_code.name, end=' ')
    traceback = sys.exc_info()[2]
    print("[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno))
    print(traceback.print_tb())
    
def getByteCounter(p4info_helper, sw, counter_name, index):
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            return entity.counter_entry.data.byte_count

def setupBalancingSwitch(p4info_helper, bmv2_file_path):
    sw = p4runtime_lib.bmv2.Bmv2SwitchConnection(
        name='s1',
        address='127.0.0.1:50051',
        device_id=0,
        proto_dump_file='logs/s1-p4runtime-requests.txt')


    # Send master arbitration update message to establish this controller as
    # master (required by P4Runtime before performing any other write operation)
    sw.MasterArbitrationUpdate()

    # Install the P4 program on the switches
    sw.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                    bmv2_json_file_path=bmv2_file_path)
    print("Installed load balancing P4 Program using SetForwardingPipelineConfig on s1")

    # Setup initial table rules
    writeEcmpGroupValues(p4info_helper, sw)
    # TODO 8) Call writeEcmpNextHopRules with a 50/50 entry_amounts and update_type=p4info_helper.UpdateType.INSERT
    writeEgressSendFrameRules(p4info_helper, sw)
    writeEcmpNextHopRules(p4info_helper, sw, (50, 50), update_type=p4info_helper.UpdateType.INSERT)
    return sw

def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        sw = setupBalancingSwitch(p4info_helper, bmv2_file_path)

        # Uncomment the following line to read table entries
        #readTableRules(p4info_helper, sw)

        while True:
            sleep(2)
            
            # TODO 
            # 9.1) Use getByteCounter to read out the counters for each link
            #    Uncomment:
            c1 = getByteCounter(p4info_helper, sw, "MyIngress.enlace", 0)
            c2 = getByteCounter(p4info_helper, sw, "MyIngress.enlace", 1)
            entry_amounts = balanceEntryAmounts(c1, c2)
            
            
            # TODO 
            # 9.2) Call writeEcmpNextHopRules with the entry amounts provided 
            # by balanceEntryAmounts and with update_type=p4info_helper.UpdateType.MODIFY
            
            # Uncomment the following line to read table entries
            #readTableRules(p4info_helper, sw)
            
            # Uncomment the following line to print the current entry_amounts and loads.
            print(f"load to h2: {c1}; load to h3: {c2}; balancing ratio: {entry_amounts}")

            writeEcmpNextHopRules(p4info_helper, sw, entry_amounts, update_type=p4info_helper.UpdateType.MODIFY)


    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c from load_balance.p4',
                        type=str, action="store", required=False,
                        default='./build/load_balance.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4 from load_balance.p4',
                        type=str, action="store", required=False,
                        default='./build/load_balance.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)
    main(args.p4info, args.bmv2_json)
