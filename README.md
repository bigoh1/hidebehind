hidebehind
=====
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![GitHub issues](https://img.shields.io/github/issues-raw/multifrench/hidebehind)](https://github.com/multifrench/cover/issues)
[![Code of Conduct](https://img.shields.io/badge/code%20of-conduct-ff69b4.svg?style=flat)](https://github.com/multifrench/hidebehind/blob/main/CODE_OF_CONDUCT.md)

What is this?
=============
It's a simple python library to embed data (files) into image/video/audio files.

Why?
=======
It was written for educational purposes only. It may contain bugs, so use it at your own risk!

Installation
============
```bash
$ python3 -m pip install hidebehind
# Create an alias for it. Note, if you use zsh, change .bashrc to .zshrc 
$ cp ~/.bashrc ~/.bashrc.bak && echo "alias hide='python3 -m hidebehind'" >> ~/.bashrc && source ~/.bashrc 
```

Quick start examples
====================
First, read [Unix philosophy](https://en.wikipedia.org/wiki/Unix_philosophy#Origin):
> Write programs to handle text streams, because that is a universal interface. 

Assume you have:
```bash
$ echo "Dream big and dare to fail" > secret1.txt
$ echo "Talk is cheap. Show me the code." > secret2.txt
$ wget https://github.com/multifrench/hidebehind/blob/main/img/Gauss.png
```
Then:
```bash
$ hide put -c Gauss.png < secret1.txt > embedded.png
$ hide get < embedded.png > s1-restored.txt
$ cat s1-restored.txt
```

Encryption
==========
It's not safe to transmit unencrypted (sensitive) information over public connections.  
In this example I'll use `GnuPG`, but you can use anything you want (i.e. `VeraCrypt`)
```bash
# Encrypt:
$ gpg -er <YouKeyID> -o - < secret2.txt | hide put -c Gauss.png > embedded.png
# Decrypt:
$ hide get < embedded.png | gpg -d > s2-restored.txt
$ cat s2-restored.txt
```

Multiple files & compression
============================
In case you want to transmit more than one file at once, use `tar`.  
It's also a good idea to compress our data. I'll use `bzip2`.
```bash
$ tar -c secret?.txt | bzip2 -9 | hide put -c Gauss.png > embedded.png
# And get our data back:
$ hide get < embedded.png | tar -xj
$ cat secret?.txt
```

Integrity
=========
In addition, to be sure our files weren't corrupted, we will write down their hashes (`sha256sum`) into a separate file and use technique from the previous paragraph to save them.
```bash
$ sha256sum secret?.txt > .shasum
# Copy-paste the previous code block but add `.shasum` into the archive.
$ tar -c secret?.txt .shasum | bzip2 -9 | hide put -c Gauss.png > embedded.png
# Get our data back:
$ hide get < embedded.png | tar -xj
# Now, verify the data wasn't corrupted (or it was)
$ sha256sum -c .shasum
```

What else?
=====================
> Write programs to handle text streams, because that is a universal interface.

Remember? I hope now you're (if you weren't) convinced it's very useful technique. 
You may, for example, want to embed encrypted and compressed secret and then check its integrity. It's up to you.




How does it work?
=================
Do you see the difference?

![A square](https://github.com/multifrench/hidebehind/blob/main/img/square.png)
![The square with embedded message in it](https://github.com/multifrench/hidebehind/blob/main/img/square-embedded.png)

Nor do I. But there is a secret embedded in it!
> Stay hungry. Stay foolish

Basically, the idea behind it is that **the human eye is very insensitive**. It can't detect difference in less than 1%.  
The program slightly changes the value of blue part (of an RGB pixel). 

<details>
  <summary>Implementation detail</summary>
  Assume we want to hide a sequence of bytes <code>S</code> (that's our secret message; it's not necessarily a string of printable characters, i.e. a binary file) into
  an image <code>I</code>. For simplicity, we assume an image is an <code>NxMx3</code> array, where <code>I[i][j]</code> is <code>[red, green, blue]</code>. We are only interested in <code>0 <= blue < 256</code> value.
  It's possible to represent it as a binary number. For example, <code>55 = 0b110111</code>. If we clear last least significant bit, we get <code>0b110110 = 54</code>. We changed the value of it only by less than <code>0.4%</code>!  
  Having done so, now we can store the payload there. Yes, a bit of the payload goes into one pixel. If we want to embed more, we modify two least significant bits. The maximum difference then will be <code>1.2%</code>, but it's still OK.
</details>
