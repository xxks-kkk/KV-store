# *Daadkvs* as a Distributed Key-Value Store

We implement a distributed key-value store called *Daadkvs* (**D**aadkvs **a**s **a** 
**D**istributed **K**ey-**V**alue **S**tore). *Daadkvs* implements an eventually consistency model.
Each entry in the store will be a pair of binary strings. The system will consist of clients and servers.
Servers will store the data and perform updates when asked by the clients. Clients will be able
to perform the following operations:

- **Put**:​ a new entry into the store.
- **Get**:​ the value associated with a key

In addition, we provide two session guarantees:

- *Read Your Writes*: if a client has written a value to a key, it will never read an older value.
- *Monotonic Reads*: if a client has read a value, it will never read an older value.

## Implementation

The architecture of our implementation is shown in image below. In the picture, the modules
of the code (i.e., *Master*, *Clients*) are represented by the boxes. The actual source code files
are listed under the module names inside parentheses. The commands are associated with colors of the modules.
For instance, the "Put" command is supported by *Clients* module (i.e., "client.py") and 
*Servers* module (i.e., "server.py"). The semantics of the commands are shown in the table following afterward. 

![architecture](img/architecture.png)

| Command                          | Summary                                                                                                                                                                                                                                                                              |
|----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| joinServer [id]                  | This command starts a server and will connect this server to all other servers in the system                                                                                                                                                                                         |
| killServer [id]                  | This command immediately kills a server. It should block until the server is stopped.                                                                                                                                                                                                |
| joinClient [clientId] [serverId] | This command will start a client and connect the client to the specified server.                                                                                                                                                                                                     |
| breakConnection [id1] [id2]      | This command will break the connection between a client and a server or between two servers.                                                                                                                                                                                         |
| createConnection [id1] [id2]     | This command will create or restore the connection between a client and a server or between two servers.                                                                                                                                                                             |
| stabilize                        | This command will block until all values are able to propagate to all connected servers. This should block for a max of 5 seconds for a system with 5 servers.                                                                                                                       |
| printStore [id]                  | This command will print out a server’s key-value store in the format described below.                                                                                                                                                                                                |
| put [clientId] [key] [value]     | This command will tell a client to associate the given value with the key. This command should block until the client communicates with one server.                                                                                                                                  |
| get [clientId] [key]             | This command will tell a client to attempt to get the key associated with the given value. The value or error returned should be printed to standard-out in the format specified below. This command should block until the client communicates with a server and the master script. |

The functionality of each module is following:

- *Master*: a master program which will provide a programmatic interface with the key-value store.
The master program will keep track of and will also send command messages to all servers and
clients. More specifically, the master program will read a sequence of newline delineated
commands from standard input ending with EOF which will interact with the key-value store and,
when instructed to, will display output from the playlist to standard output.

- *Clients*: clients program that invoked by the mater program and perform corresponding commands.
All the commands are implemented using RPC calls. In addition, clients cache the vector clock of the 
"Put" command to support *Read Your Writes*.

- *Watch dogs*: each server is guarded by a watch dog which takes command from the master to join the server
he guarded to the network or kill the server process.

- *Router*: each server gets a router which periodically receive information about the current network topology,
 it is used to find the path to all the available servers that the current server can reach.

- *Servers*: server works as a RPC server to the clients and works with *Model* to implement the gossip
proctol and handle message passing between servers.

- *Model*: model implements the actual protocol of the system. Specifically, the module implements
what string to return on "printStore", what to do on "put", and what to return to the requesters on "get".

- *Vector Clock*: as name suggested, the module implements the vector clock and decide the "happen-before"
relationship between two events. 

- *Storage*: the storage layer writes the log and the key-value pairs onto the disk. The storage is used
when one server is killed and revived later.

## Protocol

Our eventual consistency is implemented through vector clocks and guaranteed delivery (whenever possible). 
Whenever a server receives a put from clients, `put` routine inside *Model* get invoked inside `xmlrpc_put` 
from *Servers*. Inside `put`, we put the key-value pair inside the write log and start to send "Put" message 
to its peer servers using the infrastructure provided by *Servers*. Each server is responsible for managing its own "put" and propagate them to
all other servers. Therefore, each server manage a write log, it is used to keep track of whether a key-value pair 
has been successfully propagated to the rest servers. We implement this machanism by having each server receiving 
the internal "Put" message return an "Ack" to its sender. If a message is acked by all its peer servers, we delete 
the entry from the write log. The server periodically checks its write log and resend "Put" message to its peer servers
in case of network partition and node failure.
 
There are three type of internal message among the servers. 

The first message type is "Put" (This different from the xmlrpc\_put interface provided to client). For the peer 
server, whenever we receive a message from peers, we check if the message's target server
(`ReceiverId`) is itself. If it is, we invoke *Model*'s `put_internal` routine. This routine check if the K-V pair
is more recent than its current K-V pair by the corresponding (server\_id, vector\_clock) pair. If we receive a more recent
K-V value, we update the local key-value pair in local storage. Under both conditions, send out the "ACK" message back to 
the server that receive. Otherwise, we redirect the message to other peers based on the information provided by the router.

The second message type is "Ack", this message is sent when other servers receives "Put" message from it. On receiving such
message, server set the corresponding bit of the receiptVector from the write log. If all five bits of the receiptVector are set,
the entry is removed from write log.

Beyond handling the "Put" and "Ack", the protocol also periodically send out heart beat messages (`Gossip` in *Servers*) 
to the peers with its current knowlege of system time (clocks). In addition, we exchange the topology of the networks (i.e., 
neighbors that each server can connect) through message with type `"Gossip". The messages are feed into routers module
to give itself with a up-to-date view of the network topology.
 
## Tests and Performance

Our sytem is designed towards a scenario that there are five clients and each of them will connect to one
of five servers. The clients will rotate issuing put requests and then "stabilize" command will be invoked
at the end.

We design two test environments and the test results are reported in the table below. We list all test cases
and report the performance only on the benchmark test cases.

- Single machine: we spawn all clients and servers on a single machine and we issue the commands from the pre-generated 
test cases (using "commandGen.py").

- Multiple machines: we use 10 machines with each machine hosts a server or a client. We issue the commands
from the pre-generated test cases (using "commandGen.py").

We use UTCS lab machines: Intel Xeon 3.60GHz CPU with 16 GB RAM, 240 GB SATA Disk with Ubuntu 16.04.3 LTS 
to conduct all of our tests.


| Test case                | Test Description                                                                                                                                                                                                                                           | Test Environment | Workload       | Data Size | Throughput               |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|----------------|-----------|--------------------------|
| command-tree-4000.txt    | All the servers are connected in a tree structure. It is used to test the *Router* module                                                                                                                                                                  | Single           | 4026 commands  | 3.1M      | 351.84 requests / second |
| command{1-15}.txt        | Basic module logic tests                                                                                                                                                                                                                                   | Single           | NA             | NA        | NA                       |
| command{21-24}-4000.txt  | Basic module logic tests in heavy workloads                                                                                                                                                                                                                | Single           | 4026 commands  | 3.1M      | NA                       |
| commandComplex.txt       | Make the servers in chain topology; add server one by one and test whether a newly-joined server can get the data from other servers asynchronously; kill one of servers and let it rejoin the network and see whether we can achieve eventual consistency | Single           | 9031 commands  | 16M       | 367.13 requests / second |
| commandPartitionTiny.txt | Create the network partition among servers and then reform the fully-connected network. It is used to test out the eventual consistency model when network partition happens.                                                                              | Single           | NA             | NA        | NA                       |
| commandPartition.txt     | Benchmark version for commandPartitionTiny.txt                                                                                                                                                                                                             | Single           | 25032 commands | 215M      | 292.02 requests / second |

## How to use our system

- Install the dependency through `make setup`
- The server ids should be named by integer 0 - 9. 0 - 4 is server ids and 5 - 9 is client ids. Inside config.py set the five
client and server rpc port in the variable ADDR\_PORT, its content should be self explanatory. You should also set the 5 port
for server watchdog to listen to master command.
- open a terminal on each machine or multiple terminal window on the same machine. On the five server terminal, set cwd to 
the project directory, then run "python watchdog -p {WATCHDOG\_PORT}" (server will be started by watchdog when requested from
 master). On the five client terminal, set cwd to the project directory, then run "python client -p {CLIENT\_PORT}". CLIENT\_PORT
 and SERVER\_PORT should be consistent with the information recorded in config.py.
- Open another terminal in the same network (could be one of the servers or clients), set cwd to the project directory, type
"python master.py". Then the program will wait for your input from STDIN with commands specified by the API specification.
- To expedite testing, we can redirect test script from stdin to the master program by typing "python master.py < {PATH\_TO\_TEST\_SCRIPT}".


## Authors (listed in alphabetical order of last name)

- Jianwei Chen @JianweiCxyz (UT EID: jc83978 UTCS id: jwchen)
- Zeyuan Hu @xxks-kkk (UT EID: zh4378 UTCS id: zeyuanhu)
- Wei Sun @sunwell1994 (UT EID: ws8699; UTCS id:weisun )
