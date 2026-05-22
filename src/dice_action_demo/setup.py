from setuptools import setup

package_name = 'dice_action_demo'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'dice_server = dice_action_demo.server:main',
            'dice_client = dice_action_demo.client:main',
        ],
    },
)
