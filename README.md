# Judge-Microservice
配置驅動的 Judge 微服務，以隔離、無狀態、靈活配置為主

## Ubuntu 設定 SSH

### 生成 SSH 公司鑰匙

```bash
ssh-keygen -t rsa -b 4096 -C "yourmail@example.com"
```

### 預設路徑，`id_rsa`為私鑰、`id_rsa.pub`為公鑰

```bash
Your identification has been saved in /home/tsukisama9292/.ssh/id_rsa
Your public key has been saved in /home/tsukisama9292/.ssh/id_rsa.pub
```

### 將公鑰複製到遠端伺服器

```bash
ssh-copy-id username@remote_host
```

`username`：遠端伺服器的使用者名稱
`remote_host`：遠端伺服器的 IP 位址或主機名稱

###

```
cat ~/.ssh/id_rsa.pub | ssh tsukisama9292@127.0.0.1 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'
```
