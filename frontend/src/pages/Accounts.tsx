import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, Form, Input, Switch, message, Popconfirm, Card } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SyncOutlined, ReloadOutlined } from '@ant-design/icons';
import { accountApi } from '../api';
import { XHSAccount, XHSAccountCreate } from '../types';

const Accounts: React.FC = () => {
  const [accounts, setAccounts] = useState<XHSAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingAccount, setEditingAccount] = useState<XHSAccount | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [form] = Form.useForm();

  const fetchAccounts = async () => {
    setLoading(true);
    try {
      const response = await accountApi.list({ page, page_size: 20 });
      setAccounts(response.data || []);
      setTotal(response.data?.length || 0);
    } catch (error) {
      message.error('获取账号列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, [page]);

  const handleAdd = () => {
    setEditingAccount(null);
    form.resetFields();
    form.setFieldsValue({
      monitor_comments: true,
      monitor_messages: false,
      is_active: true
    });
    setModalVisible(true);
  };

  const handleEdit = (record: XHSAccount) => {
    setEditingAccount(record);
    form.setFieldsValue({
      ...record,
      monitor_note_ids: record.monitor_note_ids || '',
      ignored_users: record.ignored_users || ''
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await accountApi.delete(id);
      message.success('删除成功');
      fetchAccounts();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingAccount) {
        await accountApi.update(editingAccount.id, values);
        message.success('更新成功');
      } else {
        await accountApi.create(values);
        message.success('添加成功');
      }
      
      setModalVisible(false);
      fetchAccounts();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  const handleRefreshCookie = (record: XHSAccount) => {
    form.setFieldsValue({
      name: record.name,
      cookie_web_session: record.cookie_web_session,
      cookie_a1: record.cookie_a1
    });
    setEditingAccount(record);
    setModalVisible(true);
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60
    },
    {
      title: '账号名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '小红书昵称',
      dataIndex: 'nickname',
      key: 'nickname',
      render: (val: string) => val || '-'
    },
    {
      title: '登录状态',
      dataIndex: 'login_status',
      key: 'login_status',
      render: (status: string) => {
        const config = {
          valid: { color: 'green', text: '正常' },
          invalid: { color: 'red', text: '失效' },
          expired: { color: 'orange', text: '过期' },
          unknown: { color: 'default', text: '未知' }
        };
        const c = config[status as keyof typeof config] || config.unknown;
        return <Tag color={c.color}>{c.text}</Tag>;
      }
    },
    {
      title: '监控评论',
      dataIndex: 'monitor_comments',
      key: 'monitor_comments',
      render: (val: boolean) => val ? <Tag color="blue">是</Tag> : <Tag>否</Tag>
    },
    {
      title: '监控私信',
      dataIndex: 'monitor_messages',
      key: 'monitor_messages',
      render: (val: boolean) => val ? <Tag color="blue">是</Tag> : <Tag>否</Tag>
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (val: boolean) => val ? <Tag color="green">启用</Tag> : <Tag>禁用</Tag>
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: XHSAccount) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button type="link" size="small" icon={<SyncOutlined />} onClick={() => handleRefreshCookie(record)}>
            刷新Cookie
          </Button>
          <Popconfirm title="确定删除此账号？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            添加账号
          </Button>
          <Button icon={<ReloadOutlined />} onClick={fetchAccounts} style={{ marginLeft: 8 }}>
            刷新
          </Button>
        </div>
        
        <Table
          columns={columns}
          dataSource={accounts}
          rowKey="id"
          loading={loading}
          pagination={{ current: page, pageSize: 20, total, onChange: setPage }}
        />
      </Card>

      <Modal
        title={editingAccount ? '编辑账号' : '添加账号'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="账号名称" rules={[{ required: true, message: '请输入账号名称' }]}>
            <Input placeholder="用于识别账号的备注名称" />
          </Form.Item>
          
          <Form.Item name="cookie_web_session" label="Cookie (web_session)" rules={[{ required: true, message: '请输入web_session' }]}>
            <Input.TextArea rows={2} placeholder="小红书web_session Cookie" />
          </Form.Item>
          
          <Form.Item name="cookie_a1" label="Cookie (a1)" rules={[{ required: true, message: '请输入a1' }]}>
            <Input.TextArea rows={2} placeholder="小红书a1 Cookie" />
          </Form.Item>
          
          <Form.Item name="monitor_note_ids" label="监控笔记ID">
            <Input.TextArea rows={2} placeholder="指定监控的笔记ID，多个用逗号分隔，留空则监控所有笔记" />
          </Form.Item>
          
          <Form.Item name="ignored_users" label="忽略用户">
            <Input.TextArea rows={2} placeholder="忽略的用户ID，多个用逗号分隔" />
          </Form.Item>
          
          <Form.Item name="monitor_comments" label="监控评论" valuePropName="checked">
            <Switch />
          </Form.Item>
          
          <Form.Item name="monitor_messages" label="监控私信" valuePropName="checked">
            <Switch />
          </Form.Item>
          
          <Form.Item name="is_active" label="启用账号" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Accounts;