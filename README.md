# Ceres :rice: :dollar:

加班餐费报销登记号后台

## 部署

### 安装 Conda

```
$ wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
$ bash Miniconda2-latest-Linux-x86_64.sh
```

### 创建和启动虚拟环境

下载代码，并创建虚拟环境

```
$ git clone git@github.com:xiachufang/Ceres.git

$ conda env create -f Ceres/environment.yml
$ source activate ceres
```

### 之后更新虚拟环境

开发环境导出：

```
$ conda env export > environment.yml
```

线上对应更新：

```
$ conda env update -f environment.yml
```

### 配置 Config 和环境变量

参照 `ceres/config/sample_config.py` 写对应的 config 文件，并设置环境变量 `CERES_APP_CONFIG='ceres.config.<config-file-model-name>'`

其他环境变量：

```
export PATH="/home/ceres/miniconda2/bin:$PATH"
source activate ceres
export PYTHONPATH="/home/ceres/Ceres"
```

### 创建数据库

```
python Ceres/ceres/tool/create_databases_and_tables.py
```

## TODO

- [ ] 回复「报销单」和「月报销单」时候的回复优化，加时间段，没内容时做处理
- [ ] 加公众号菜单
- [ ] 生成汇总 Excel
- [ ] 默认只能加入当天的报销单（有需要可以后缀 “!” 强制操作）
