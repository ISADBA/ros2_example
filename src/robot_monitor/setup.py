from setuptools import setup

package_name = 'robot_monitor'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='isadba',
    maintainer_email='isadba@example.com',
    description='ROS2 Jazzy Robot Monitor Demo',
    license='Apache License 2.0',

    data_files=[

        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),

        (
            'share/' + package_name,
            ['package.xml'],
        ),

        (
            'share/' + package_name + '/launch',
            ['launch/monitor.launch.py'],
        ),
    ],

    tests_require=['pytest'],

    entry_points={
        'console_scripts': [

            'status_publisher = robot_monitor.status_publisher:main',

            'status_subscriber = robot_monitor.status_subscriber:main',
        ],
    },
)
