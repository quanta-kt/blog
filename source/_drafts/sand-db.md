---
title: "SandDB: An immutable, persistent key-value store"
date: 2025-08-20
---

## Motivation

I had just began to cook my *super secret* project for which I needed an
embedded data store to back my data.

Now, I _could_, use a well known and well supported solution. But hey, that's
not very fun, is it?

I decided I will write my own. Not because this was an "unsolved" problem, but
just because I thought "how hard could it be to roll by own key-value
database?".

I had recently read up some litrature on building simple databases from various
sources and really wanted to give it a try. The whole process has been very
rewarding. I might even give building a relational database a shot in future.

## Goals

My goals for the store (from the orignal use-case) are:

* Very fast writes single and batch writes.
* Reasonably fast point reads.
* Reasonably fast range scans.

## Non goals

* Deletion: I wanted an append-only, immutable store. I did not need a delete
  operation.
* Foreign keys: I only wanted to read and write a bunch of values quickly. I did
  not need a way to reference one datum from another. Well, at least not in a
  way the store should be aware of.

## Inspiration

### Git's reftable

Git has traditionally used files under `.git/refs` to store refs ("loose refs").
This is simple and worked, however some large repositories such as android and
rails had way too many refs and lookup was noticeably slow.

Other problems with loose refs include:

* They occupy a large number of disk blocks
* Batch reads are penalized by large number of syscalls.

It should be noted that git also had the "packed ref" format as an alternative
but it had its own problems:

* Single lookup requires linearly scanning the file.
* Atomic writes required copying the entire packed ref file for even small
  transactions.

This lead to the development of the new reftable format which employs an
LSM-tree-like storage engine. The performance gains are massive in terms of both
query time and storage.

For more information, see [reftable page](https://git-scm.com/docs/reftable)
in git's documentation.

This facinated me and I dived a little bit into the design and implemenation
details of this new format.

### RocksDB

While looking around the ideas and techniques behind the reftable format, I
found a few more key-value databases. The one that perticularly stood out to be
was RocksDB. Reading about it, I discovered the concept of Log Structured Merge
trees (LSM trees).

I also named this project SandDB because I was inspired from RocksDB.

## Log-structured-merge-trees

The core and heart of SandDB is LSM tree. A data structure designed for very
fast writes.

LSM trees have a tiered storage model where each tier/level is more "permanent".

### Memtable

The first level is (usually) backed by an in-memory data structure. This is
called a "memtable". SandDB uses Rust's `BTreeMap` (for no other reason than
it is readily available for use in the language).

All the new writes are added to the memtable and no files are touched.

If you can't tell, this is *very* fast since we inherit `BTreeMap`'s insertion
time complexity i.e. O(log n) where n is the height of B+Tree.

### SSTables

Of course, entries in the memtable will eventually have to be written to files
in order for the store to be persistent.

Once the memtable reaches a certain threshold, it is flushed to an SSTable file.
This is an immutable file i.o.w, once created it is never modified.

We must also flush the memtable to an SSTable when the database exits so that we
don't lose any entries.

SSTables are binary files. I have documented it's format [here](https://github.com/quanta-kt/SandDB/blob/master/docs/sst-file-spec.md)
if you are interested.

### Compaction

Now since we create a new SSTable on each flush, we will inevitably end up with
several such files over time. This can be a problem for querying as we might end
up having to scan a lot of different files. Opening files also add to our
number of syscalls per query.

We must therefore occasionally _compact_ our SSTables, i.e. merge smaller
SSTables into a larger ones.

SSTables are tiered. When a memtable is flushed, a level 0 SSTable is created.
When we have "way too many" SSTables, we initiate a compaction: gather all level
0 SSTables and merge them into a single level 1 SSTable.

When we have enough level 1 SSTables, we merge them to level 2. At the time of
writing, SandDB only merges upto level 2. We also merge several level 2 SSTables
into one if there are too many of them.

We only pay the cost of compaction once in a while.

### Manifest

An additional file called manifest is kept around to track the SSTables and
their metadata. It includes:

* ID of the manifest file, using which we can derive the filename.
* It's level.
* The key range.

Each time an SSTable is added or removed, the manifest is updated to reflect
the same.

When querying, the reader looks at the manifest and figures out which SSTables
might contain the key it is looking for and reads those in the order of their
(ID, level). The ordering matters because we want to ensure we look in the most
recently written SSTables first.

We only open the SSTables which the manifest tells us might contain our key.
This way we don't have to open every single SSTable and we save reads and
syscalls.

We can also go beyond having a key range and add per-SSTable
[bloom filters](https://en.wikipedia.org/wiki/Bloom_filter)
in the manifest. This would further reduce the number of files we would have to
open and read. I plan to implement this sometime later in future.

The manifest file is a WAL-style file. When a new SSTable is added, an entry
saying "added sst x" is appended to the file. Similarly, when an SSTable is
deleted, an entry saying "deleted sst x" is inserted.

Why do this instead of rewriting the manifest? For atomicity (and possibly for
isolation, in future).

If we replace the entire contents of manifest instead of appending, a reader in
the middle of reading manifest might end up reading first half of the file
before the sst was added and the later half after.

I will admit that SandDB does not yet allow concurrent read/write, however I do
see myself sitting down to implement it in future. Soon (TM).

I have documented manifest file's format here
[here](https://github.com/quanta-kt/SandDB/blob/master/docs/manifest-file-spec.md)
if you are interested.

