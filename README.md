# 🗳️ Verificatum Java API

This project is a Java-based RESTful API built with Spring Boot to interact with the [Verificatum Mix-Net](https://www.verificatum.org/) using internal library calls rather than shelling out to CLI commands. It’s intended to power e-voting systems with mobility, threshold mix-nets, and future-ready support for asynchronous execution across multiple mix-servers.

## 🚀 Features

- Full Java integration with Verificatum’s internal library (no CLI required)
- Endpoint for protocol stub file generation (`-prot`)
- Spring Boot API, ready to integrate with frontends or orchestrators

## 📦 Requirements

| Tool       | Version |
|------------|---------|
| Java       | 17      |
| Maven      | 3.x     |
| Git        | latest  |
| Curl       | optional for API testing |
| Linux      | required for native `.so` dependencies |


## ⚙️ ⚙️ Clone, Build & Setup

```bash
git clone https://github.com/YOUR_USERNAME/verificatum-api.git
cd verificatum-api
```

### ✅ One-Time Native Library Setup (REQUIRED)

> Verificatum depends on a native library (libvecj-2.2.0.so) that must be accessible at runtime. Without this, the API will crash with java.lang.UnsatisfiedLinkError.

Run this inside the project folder:

```bash
export LD_LIBRARY_PATH=$(pwd)/lib:$LD_LIBRARY_PATH
```

To make it permanent (optional):

```bash
echo 'export LD_LIBRARY_PATH=$(pwd)/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

## 🛠️ Build & Run

```bash
mvn clean install
mvn spring-boot:run
```
The API will be available at:

`http://localhost:8080`

## 📡 API Endpoints
### ➕ Generate Stub File

**GET** `/verificatum/generate-stub`

Generates a protocol stub (stub.xml) using internal Verificatum library functions (equivalent to vmni -prot).

📝 Output will appear in the root of the project (verificatum-api/stub.xml).

## 🔜 Next Steps

- Add endpoints for -party and -merge phases of vmni

- Allow parameterized requests for all fields

- Automate setup for multiple mix-servers (3 or more)

- Clean up and modularize configurations for LAN or distributed deployments

- Start writing integration tests and performance benchmarking