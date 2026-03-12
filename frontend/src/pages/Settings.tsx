import React, { useState } from 'react';
import { Card, Form, Input, Button, Upload, Avatar, message, Tabs, Switch, Select, Space, Typography } from 'antd';
import { UserOutlined, UploadOutlined, SaveOutlined } from '@ant-design/icons';
import { useAuthStore } from '../stores/auth';
import { userApi, authApi } from '../api';

const { Title, Text } = Typography;

const Settings: React.FC = () => {
  const { user, updateUser } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();

  const handleProfileUpdate = async (values: any) => {
    setLoading(true);
    try {
      const response = await userApi.update(values);
      updateUser(response.data);
      message.success('个人信息更新成功');
    } catch (error) {
      message.error('更新失败');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (values: any) => {
    if (values.new_password !== values.confirm_password) {
      message.error('两次输入的密码不一致');
      return;
    }
    setLoading(true);
    try {
      await authApi.changePassword(values);
      message.success('密码修改成功');
      passwordForm.resetFields();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '修改失败');
    } finally {
      setLoading(false);
    }
  };

  const tabItems = [
    {
      key: 'profile',
      label: '个人信息',
      children: (
        <Card>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 32 }}>
            <Avatar size={80} icon={<UserOutlined />} src={user?.avatar} />
            <div style={{ marginLeft: 24 }}>
              <Upload showUploadList={false}>
                <Button icon={<UploadOutlined />}>更换头像</Button>
              </Upload>
            </div>
          </div>
          
          <Form
            form={profileForm}
            layout="vertical"
            initialValues={{
              nickname: user?.nickname,
              email: user?.email,
              phone: user?.phone,
              bio: user?.bio
            }}
            onFinish={handleProfileUpdate}
          >
            <Form.Item name="nickname" label="昵称">
              <Input />
            </Form.Item>
            <Form.Item name="email" label="邮箱">
              <Input type="email" />
            </Form.Item>
            <Form.Item name="phone" label="手机号">
              <Input />
            </Form.Item>
            <Form.Item name="bio" label="个人简介">
              <Input.TextArea rows={3} />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading}>
                保存修改
              </Button>
            </Form.Item>
          </Form>
        </Card>
      )
    },
    {
      key: 'security',
      label: '安全设置',
      children: (
        <Card>
          <Title level={4}>修改密码</Title>
          <Form
            form={passwordForm}
            layout="vertical"
            onFinish={handlePasswordChange}
            style={{ maxWidth: 400 }}
          >
            <Form.Item name="old_password" label="当前密码" rules={[{ required: true }]}>
              <Input.Password />
            </Form.Item>
            <Form.Item name="new_password" label="新密码" rules={[{ required: true, min: 6 }]}>
              <Input.Password />
            </Form.Item>
            <Form.Item name="confirm_password" label="确认新密码" rules={[{ required: true }]}>
              <Input.Password />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading}>
                修改密码
              </Button>
            </Form.Item>
          </Form>
        </Card>
      )
    },
    {
      key: 'notifications',
      label: '通知设置',
      children: (
        <Card>
          <Title level={4}>通知偏好</Title>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Text strong>邮件通知</Text>
                <br />
                <Text type="secondary">接收账号状态变更、规则匹配等通知</Text>
              </div>
              <Switch defaultChecked />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Text strong>回复成功通知</Text>
                <br />
                <Text type="secondary">每条回复成功后发送通知</Text>
              </div>
              <Switch />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Text strong>Webhook通知</Text>
                <br />
                <Text type="secondary">通过Webhook推送回复记录</Text>
              </div>
              <Switch />
            </div>
          </Space>
        </Card>
      )
    },
    {
      key: 'api',
      label: 'API设置',
      children: (
        <Card>
          <Title level={4}>API访问</Title>
          <Text type="secondary">专业版及以上套餐支持API访问</Text>
          <div style={{ marginTop: 24 }}>
            <Text strong>API Key</Text>
            <Input.Password 
              value="sk-xxxx-xxxx-xxxx-xxxx" 
              readOnly 
              style={{ marginTop: 8 }}
              addonAfter={<Button type="text" size="small">复制</Button>}
            />
            <Button style={{ marginTop: 16 }}>重新生成API Key</Button>
          </div>
        </Card>
      )
    }
  ];

  return (
    <div>
      <Tabs items={tabItems} />
    </div>
  );
};

export default Settings;