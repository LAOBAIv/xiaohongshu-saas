import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, Form, Input, Select, Switch, message, Popconfirm, Card, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { ruleApi, accountApi } from '../api';
import { ReplyRule, ReplyRuleCreate, XHSAccount } from '../types';

const { TextArea } = Input;

const Rules: React.FC = () => {
  const [rules, setRules] = useState<ReplyRule[]>([]);
  const [accounts, setAccounts] = useState<XHSAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRule, setEditingRule] = useState<ReplyRule | null>(null);
  const [form] = Form.useForm();

  const fetchRules = async () => {
    setLoading(true);
    try {
      const response = await ruleApi.list();
      setRules(response.data || []);
    } catch (error) {
      message.error('获取规则列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchAccounts = async () => {
    try {
      const response = await accountApi.list({ page_size: 100 });
      setAccounts(response.data || []);
    } catch (error) {
      console.error('获取账号列表失败', error);
    }
  };

  useEffect(() => {
    fetchRules();
    fetchAccounts();
  }, []);

  const handleAdd = () => {
    setEditingRule(null);
    form.resetFields();
    form.setFieldsValue({
      rule_type: 'comment',
      match_type: 'fuzzy',
      priority: 1,
      is_enabled: true,
      use_ai_reply: false
    });
    setModalVisible(true);
  };

  const handleEdit = (record: ReplyRule) => {
    setEditingRule(record);
    form.setFieldsValue({
      ...record,
      keywords: record.keywords.split(',').join(', '),
      reply_templates: record.reply_templates.split('\n').join('\n')
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await ruleApi.delete(id);
      message.success('删除成功');
      fetchRules();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      // 格式化数据
      const data = {
        ...values,
        keywords: values.keywords.replace(/,\s*/g, ','),
        reply_templates: values.reply_templates.trim()
      };
      
      if (editingRule) {
        await ruleApi.update(editingRule.id, data);
        message.success('更新成功');
      } else {
        await ruleApi.create(data);
        message.success('添加成功');
      }
      
      setModalVisible(false);
      fetchRules();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  const handleToggleEnable = async (record: ReplyRule) => {
    try {
      await ruleApi.update(record.id, { is_enabled: !record.is_enabled });
      message.success(record.is_enabled ? '已禁用' : '已启用');
      fetchRules();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60
    },
    {
      title: '规则名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '类型',
      dataIndex: 'rule_type',
      key: 'rule_type',
      render: (type: string) => (
        <Tag color={type === 'comment' ? 'blue' : 'green'}>
          {type === 'comment' ? '评论' : '私信'}
        </Tag>
      )
    },
    {
      title: '匹配方式',
      dataIndex: 'match_type',
      key: 'match_type',
      render: (type: string) => {
        const config = {
          exact: '精确',
          fuzzy: '模糊',
          semantic: '语义'
        };
        return <Tag>{config[type as keyof typeof config] || type}</Tag>;
      }
    },
    {
      title: '关键词',
      dataIndex: 'keywords',
      key: 'keywords',
      render: (val: string) => (
        <span style={{ maxWidth: 200, display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {val}
        </span>
      )
    },
    {
      title: '匹配次数',
      dataIndex: 'match_count',
      key: 'match_count',
    },
    {
      title: '回复次数',
      dataIndex: 'reply_count',
      key: 'reply_count',
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80
    },
    {
      title: '状态',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      render: (val: boolean, record: ReplyRule) => (
        <Switch 
          checked={val} 
          onChange={() => handleToggleEnable(record)} 
          checkedChildren="启用"
          unCheckedChildren="禁用"
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: ReplyRule) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm title="确定删除此规则？" onConfirm={() => handleDelete(record.id)}>
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
            添加规则
          </Button>
          <Button icon={<ReloadOutlined />} onClick={fetchRules} style={{ marginLeft: 8 }}>
            刷新
          </Button>
        </div>
        
        <Table
          columns={columns}
          dataSource={rules}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Modal
        title={editingRule ? '编辑规则' : '添加规则'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={700}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="name" label="规则名称" rules={[{ required: true, message: '请输入规则名称' }]}>
                <Input placeholder="如：价格咨询回复" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="account_id" label="所属账号">
                <Select placeholder="不选择则对所有账号生效" allowClear>
                  {accounts.map(acc => (
                    <Select.Option key={acc.id} value={acc.id}>{acc.name}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="rule_type" label="规则类型" rules={[{ required: true }]}>
                <Select>
                  <Select.Option value="comment">评论回复</Select.Option>
                  <Select.Option value="private_message">私信回复</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="match_type" label="匹配方式">
                <Select>
                  <Select.Option value="exact">精确匹配</Select.Option>
                  <Select.Option value="fuzzy">模糊匹配</Select.Option>
                  <Select.Option value="semantic">语义匹配</Select.Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item name="keywords" label="关键词" rules={[{ required: true, message: '请输入关键词' }]}>
            <TextArea rows={2} placeholder="多个关键词用逗号分隔，如：多少钱，价格，怎么卖" />
          </Form.Item>
          
          <Form.Item name="reply_templates" label="回复模板" rules={[{ required: true, message: '请输入回复模板' }]}>
            <TextArea rows={4} placeholder="多个回复用换行分隔，系统会随机选择一条回复" />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="priority" label="优先级">
                <Input type="number" min={1} max={100} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="is_enabled" label="启用规则" valuePropName="checked">
                <Switch defaultChecked />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="use_ai_reply" label="AI智能回复" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item name="ai_prompt" label="AI提示词（可选）">
            <TextArea rows={2} placeholder="当启用AI回复时，可以自定义AI回复的行为提示" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Rules;