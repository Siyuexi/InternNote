# Tencent_DevNote

2021.06.25-Unknown

Shenzhen,China

gestaltxu@tencent.com

## Knowledge

### Activity

#### Activity生命周期

![activity.gif](res/activity.gif.png)

- onResume()：Acitvity运行主方法
- Activity被创建：调用**onCreate()**->onStart()->onResume
- Activity被其他Activity覆盖其上：调用onPause()；Activity被重新放在顶层：调用onResume()
- Activity被锁屏或放入后台：调用onPause()->onStop()；Activity解锁或从后台唤出：调用**onRestart()**->onStart()->onResume()；
- Activity被关闭或退出：调用onPause()->onStop()->**onDestroy**



#### Activity启动模式

**Activity Stack**	返回栈，是Activity任务按照Activity调用顺序排列的栈

- 当前Activity启动另一个Activity时，新Activity会被推送到堆栈顶部，老Activity停止并被压栈在新Activity下
- 返回时，新Activity出栈并被销毁，老Activity恢复状态



**Task**    任务，是一些Activity的集合，以Activity栈的形式存放（即逻辑上的返回栈）



**launchMode**    需在Activity的xml配置文件中进行配置

- stardard：创建已存在于栈内的某个Activity时，新建一个实例并放在栈顶
- singleTop：创建和栈顶相同的Activity时，复用栈顶Activity，不新建实例
- singleTask：创建已存在于栈内的ctivity时，弹出其上所有任务；否则根据taskAffinity属性，选择压入新栈或压入本栈栈顶
- singleInstance：永远根据taskAffinty属性创建新的栈，并将新Activity压入新栈

以上**复用**会回调对应Activity 的**onNewIntent()**方法



**taskAffinity**	需在Activity的xml配置文件中进行配置

用于指定该Activity被配置到哪一个Task内。默认值是本应用的包，如果在同一个包内，一系列singleTask的Activity都不配置taskAffinity，那么他们都会生成在同一个栈内（即：与应用包名相同的栈内）；如果对他们的taskAffinty进行自定义配置，那么singleTask型的新Activity将会根据taskAffinty属性，压入新栈或当前栈顶。



**xml配置示例**

+ 启动模式：单一任务
+ 压栈对象：本应用包

```xml
<activity android:name="com.example.test.SecondActivity"
             android:launchMode="singleTask"
             android:taskAffinity="com.example.test.second">
        </activity>
```



### Service

Service可以没有界面，从而作为后台进程存在。



### Content Provider



### Broadcast Receiver



### Intent



### Context



### Adapter

Adapter用于连接view和view所展示的数据，使用Adapter需要在xml和java中配置

配置xml时，需要：

- 配置view的类型
- 配置android:id="@+id/NAME_OF_THIS_VIEW"
- 配置view的样式

配置java时，需要：

- 定义需要显示的数据
- 通过xxxView = (xxxView) findViewById(R.id.NAME_OF_THIS_VIEW)查找id
- 通过构造函数传参，初始化ArrayAdapter的**item样式**和**数据**

#### ArrayAdapter 数组适配器

只能显示一行文本数据的适配器

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">
    <ListView
        android:id="@+id/ll1"
        android:layout_width="match_parent"
        android:layout_height="wrap_content">
    </ListView>
</LinearLayout>
```

```java
package com.example.test3;

import android.app.Activity;
import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.ListView;

public class MainActivity extends Activity{
//    定义要显示的数据
    private String[] datas = {"张三","李四","王五","麻子","小强"};
    private ArrayAdapter<String> adapter;
    private ListView listView;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        listView = (ListView) findViewById(R.id.ll1);
//        初始化适配器 传参表（this,item样式,数据(String)）
        adapter = new ArrayAdapter<>(this,android.R.layout.simple_expandable_list_item_1,datas);
//        使用适配器配置view
        listView.setAdapter(adapter);
    }
}
```

注意：

- 数据是**String**类型
- item样式是在java中通过**安卓提供的样式**确定的
- ArrayAdapter支持**范型**

#### SimpleAdapter 简单适配器

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">
    <ListView
        android:id="@+id/ll1"
        android:layout_width="match_parent"
        android:layout_height="wrap_content">
    </ListView>
</LinearLayout>
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
              android:layout_width="wrap_content"
              android:layout_height="wrap_content"
              android:orientation="horizontal">
    <ImageView
        android:id="@+id/image1"
        android:layout_width="100dp"
        android:layout_height="100dp"
        android:src="@mipmap/ic_launcher"
        android:layout_margin="5dp"/>
   <LinearLayout
       android:id="@+id/ll2"
       android:layout_width="match_parent"
       android:layout_height="100dp"
       android:orientation="vertical"
       android:layout_marginTop="5dp"
       android:layout_marginLeft="10dp">
       <TextView
           android:id="@+id/text1"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:text="哈哈"
           android:textSize="30sp"
           android:layout_marginTop="10dp"/>
       <TextView
           android:id="@+id/text2"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:text="哈哈哈哈哈"
           android:textSize="24dp"
           android:layout_marginTop="10dp"/>
   </LinearLayout>
</LinearLayout>
```

```java
package com.example.test3;

import android.app.Activity;
import android.os.Bundle;
import android.widget.ListView;
import android.widget.SimpleAdapter;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


public class MainActivity extends Activity{
//    这三个经常是同时出现的
    private List<Map<String,Object>> lists;
    private SimpleAdapter adapter;
    private ListView listView;
//    定义数据
    private String[] theme = {"张三","李四","王五"};
    private String[] content ={"我是张三，你好","我是李四，你好","我是王五，你好"};
    private int[] imageViews = {R.mipmap.ic_launcher,R.mipmap.ic_account,R.mipmap.ic_password};
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        listView = (ListView) findViewById(R.id.ll1);
//        准备数据源
        lists = new ArrayList<>();
        for(int i = 0;i < theme.length;i++){
            Map<String,Object> map =new HashMap<>();
            map.put("image",imageViews[i]);
            map.put("theme",theme[i]);
            map.put("content",content[i]);
            lists.add(map);
        }
//				 初始化适配器 传参(上下文对象,数据(Map的List),item样式xml文件,每个数据的键值,每个数据的样式的id)
        adapter = new SimpleAdapter(MainActivity.this,lists,R.layout.list_item
                ,new String[]{"image","theme","content"}
                ,new int[]{R.id.image1,R.id.text1,R.id.text2});
//        使用适配器配置view
        listView.setAdapter(adapter);
    }
}
```

注意：

- 数据类型需要配置成**Map**二元组，再以**List**集成
- 需要额外配置view_item的xml样式，并通过其**id**配给对应的数据

#### BaseAdapter 基础适配器

这里同样需要像SimpleAdapter一样，要同时配置view和item的xml样式(下略)

```java
package com.example.test3;

import android.content.Context;
import android.text.Layout;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;


public class MyAdapter extends BaseAdapter {
    private List<Message> Datas;
    private Context mContext;

    public MyAdapter(List<Message> datas, Context mContext) {
        Datas = datas;
        this.mContext = mContext;
    }

    /**
     * 返回item的个数
     * @return
     */
    @Override
    public int getCount() {
        return Datas.size();
    }

    /**
     * 返回每一个item对象
     * @param i
     * @return
     */
    @Override
    public Object getItem(int i) {
        return Datas.get(i);
    }

    /**
     * 返回每一个item的id
     * @param i
     * @return
     */
    @Override
    public long getItemId(int i) {
        return i;
    }

    /**
     * 暂时不做优化处理，后面会专门整理BaseAdapter的优化
     * @param i
     * @param view
     * @param viewGroup
     * @return
     */
    @Override
    public View getView(int i, View view, ViewGroup viewGroup) {
        view = LayoutInflater.from(mContext).inflate(R.layout.list_item,viewGroup,false);
        ImageView imageView = (ImageView) view.findViewById(R.id.image1);
        TextView textView1 = (TextView) view.findViewById(R.id.text1);
        TextView textView2 = (TextView) view.findViewById(R.id.text2);
        imageView.setImageResource(Datas.get(i).getImageId());
        textView1.setText(Datas.get(i).getTheme());
        textView2.setText(Datas.get(i).getContent());
//        此处需要返回view 不能是view中某一个
        return view;
    }
}
```

```java
package com.example.test3;

import android.app.Activity;
import android.os.Bundle;
import android.widget.ListView;

import java.util.ArrayList;
import java.util.List;


public class MainActivity extends Activity{
//    这三个经常是同时出现的
    private List<Message> lists;
    private MyAdapter adapter;
    private ListView listView;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        listView = (ListView) findViewById(R.id.ll1);
        lists = new ArrayList<>();
        lists.add(new Message(R.mipmap.ic_launcher,"张三","你好，我是张三"));
        lists.add(new Message(R.mipmap.ic_account,"李四","你好，我是李四"));
        lists.add(new Message(R.mipmap.ic_password,"王五","你好，我是王五"));
//			初始化适配器，传参（数据(Message的List)，this）
        adapter = new MyAdapter(lists,MainActivity.this);
        listView.setAdapter(adapter);
    }
}
```

注意：

- 一样需要设置item的xml样式
- 需要额外继承BaseAdapter，并**重写getView()方法**，在方法内通过id查找的方式初始化item
- 初始化适配器时，数据的格式是**Message**的**List**



## Project

### VLink

#### 结构

VLink是一个sdk，这里的app只是拿来做测试用的demo，sdk源码都在vlink-mobile模块内。最终该项目的sdk模块部分会打包为arr

![vlink1](res/vlink1.png)需要给不同的游戏对接，因此提前写好对应不同游戏的sdk版本(pubg,sdsj,tymy)。这需要修改vlink-mobile模块的build.gradle，设置productFlavors的buildConfigField参数来控制对应不同手游的sdk版本。

![vlink4](res/vlink4.png)

测试时，demo app的build.gradle也需要更改版本

![vlink3](res/vlink3.png)

编译前需用Build Variants选择sdk模块构建的版本。

测试时还需同时选择app demo的版本。

![vlink5](res/vlink5.png)

### SCLog

#### JNI基础

##### JNI项目结构：

![SCLog1](res/SCLog1.png)

AS的JNI项目会增加cpp目录。该目录包含native的cpp库以及CMakeList。java类内可以调用cpp库的方法。

AS新建空JNI项目，main目录下的java和cpp：

MainActivity.java:

```java
public class MainActivity extends AppCompatActivity {

    // 加载的library名称，注意：不是C++文件的名称
    static {
        System.loadLibrary("native-lib");
    }
    private ActivityMainBinding binding;
    /**
     * java中定义方法的名称，会根据包名、类名、参数、返回值类型寻找对应的C++方法
     */
    public native String stringFromJNI();
}
```

native-lib.cpp:

```C++
//对应于java中的stringFromJNI方法
extern "C" JNIEXPORT jstring JNICALL
Java_com_example_jniapplication_MainActivity_stringFromJNI(
        JNIEnv* env,
        jobject /* this */) {
    std::string hello = "Hello from C++";
  	//返回值转义为const char*
    return env->NewStringUTF(hello.c_str());
}
```

细节：

- Java部分
  Java部分主要做了两件事情：

  1. 加载动态库

     因为动态库只需要加载一次，所以一般我们会在类的静态代码块中进行加载，这样还有个好处就是早出错，早发现

     ```java
     static {
         System.loadLibrary("native-lib");
     }
     ```

  2. native函数声明

     以下声明表示这个函数是native函数，什么参数也不传，回传一个String

     ```java
     public native String stringFromJNI();
     ```

- native部分
  native函数的实现：
  函数标识：`extern "C" JNIEXPORT`
  回传值类型：`jstring`
  参数类型：自动添加了`JNIEnv*`和`jobject`

  ```cpp
  extern "C" JNIEXPORT jstring JNICALL Java_com_wsy_jnidemo_MainActivity_stringFromJNI(
      JNIEnv *env,
      jobject /* this */){
      std::string hello = "Hello from C++";
      return env->NewStringUTF(hello.c_str());
  }
  ```

`extern "C"`：声明以下编译方式为C语言编译而非C++

`JNIEXPORT`：宏，声明了函数可见性为default

`JNICALL`：宏，空的(?)

- CMakeLists部分

  ```cmake
  # 声明最低的cmake版本
  cmake_minimum_required(VERSION 3.4.1)
  # 添加一个名称叫native-lib的动态库，该库的源文件为src/main/native-lib.cpp
  add_library( native-lib # 库的名称
               SHARED # SHARED:动态库、STATIC:静态库
               src/main/native-lib.cpp # 源文件，可以是多个
               )
               
  # 寻找系统中的log库，保存在log-lib变量中
  find_library( log-lib 
                log )
                
  # native-lib这个库会去依赖log-lib这个库
  target_link_libraries( native-lib
                         ${log-lib} )
  ```



##### JNI类型转换

oracle给出了native和java的基本类型转换表：

| Java Type | Native Type | Description      |
| --------- | ----------- | ---------------- |
| boolean   | jboolean    | unsigned 8 bits  |
| byte      | jbyte       | signed 8 bits    |
| char      | jchar       | unsigned 16 bits |
| short     | jshort      | signed 16 bits   |
| int       | jint        | signed 32 bits   |
| long      | jlong       | signed 64 bits   |
| float     | jfloat      | 32 bits          |
| double    | jdouble     | 64 bits          |
| void      | void        | N/A              |



##### JNI函数注册

JNI函数的注册一般分为两种：**静态注册和动态注册**。

- 静态注册通过固定的命名规则映射Java和native函数，如：

  1. 在java中定义好将要使用的native方法：

     ```java
     public native void testCallJava(MainActivity activity)
     ```

  2. 在cpp中定义对应的native方法：

     ```cpp
     xtern "C" JNIEXPORT void JNICALL 
     Java_com_example_jniapplication_MainActivity_staticRegister(
             JNIEnv *env,
            jobject /* this */, jobject activity)
     ```

- 动态注册通过重写`JNI_OnLoad`函数，用`jint RegisterNatives(jclass clazz, const JNINativeMethod* methods, jint nMethods)`函数将Java中定义的native函数和C/C++中定义的函数进行映射，如：

  1. 在java中定义好将要使用的native方法：

     ```java
     public native String dynamicRegister();
     ```

  2. 在cpp中定义对应的native方法：

     ```cpp
     jstring dynamicRegister(JNIEnv *jniEnv, jobject obj) {
         return jniEnv->NewStringUTF("dynamicRegister");
     }
     ```

  3. 在cpp中重写`JNI_OnLoad`方法：

     ```cpp
     int JNI_OnLoad(JavaVM *javaVM, void *reserved) {
            JNIEnv *jniEnv;
       if (JNI_OK == javaVM->GetEnv((void **) (&jniEnv), JNI_VERSION_1_4)) {
           // 动态注册的Java函数所在的类
           jclass registerClass = jniEnv->FindClass("com/wsy/jnidemo/MainActivity");
           JNINativeMethod jniNativeMethods[] = {
                   //3个参数分别为 Java函数的名称，Java函数的签名（不带函数名），本地函数指针
                    {"dynamicRegister", "()Ljava/lang/String;", (void *) (dynamicRegister)}
           };
            if (jniEnv->RegisterNatives(registerClass, jniNativeMethods,
                                        sizeof(jniNativeMethods) / sizeof((jniNativeMethods)[0])) < 0) {
                return JNI_ERR;
            }
        }
        return JNI_VERSION_1_4;
     }
     ```

     

##### java签名

java和native交互时的唯一性如何确定？

- native：通过函数名、函数参数、返回类型确保唯一性
- java：通过**签名**确保唯一性：

维基百科给出如下签名解释：

> 在计算机科学中，类型签名或类型注释定义了函数，子程序或方法的输入和输出。类型签名包括参数的数量，参数的类型以及函数包含的参数的顺序。在重载解析期间通常使用类型签名来选择在许多重载函数中正确的那一项。

> 在Java虚拟机中，内部类型签名用于标识虚拟机代码级别的方法和类。
> 示例： 方法`String String.substring(int，int)`在字节码中表示为`Ljava/lang/String.substring(II)Ljava/lang/String;`。
> 方法`main()`的签名如下所示：
> `public static void main(String[] args)`
> 在反汇编的字节码中，它采用`Lsome/package/Main/main:([Ljava/lang/String;)V`的形式。
> `main()`方法的方法签名包含三个修饰符：
> `public`表示main()方法可以被任何对象调用。
> `static`表示main()方法是一个类方法。
> `void`表示main()方法没有返回值。 

简而言之，签名是把方法的函数名、参数类型、返回值类型和成员的变量名、数据类型按一定映射关系编码成一个串。

oracle给出如下映射表：

| Type Signature            | Java Type             |
| ------------------------- | --------------------- |
| Z                         | boolean               |
| B                         | byte                  |
| C                         | char                  |
| S                         | short                 |
| I                         | int                   |
| J                         | long                  |
| F                         | float                 |
| D                         | double                |
| L fully-qualified-class ; | fully-qualified-class |
| [ type                    | type[]                |
| ( arg-types ) ret-type    | method type           |

> For example, the Java method: `long f (int n, String s, int[] arr);` 
>
> has the following type signature: `(ILjava/lang/String;[I)J`



#### 调研

##### jstring

const char* 转 jstring的函数：`env->NewStringUTF()`

- 声明：jni.h

```C++
	jstring NewStringUTF(const char* byte)
```

- 实现：jni_internal.cc

```cpp
  static jstring NewStringUTF(JNIEnv* env, const char* utf) {
    if (utf == nullptr) {
      return nullptr;
    }
    ScopedObjectAccess soa(env);
    ObjPtr<mirror::String> result = mirror::String::AllocFromModifiedUtf8(soa.Self(), utf);
    return soa.AddLocalReference<jstring>(result);
  }
```

作用是根据传入的const char*对象，创建java.lang.String对象



##### const char*：

- const char* ptr：*ptr是常量（ptr指向的值不能改变）

```C++
char str[] = "hello";
char alt[] = "world";
const char* ptr = str;//const修饰char*，即指针指向的值是常量
*ptr = 'a';//报错，无法更改指向地址的值
ptr = alt;//可以，直接更改指针本身
```

- char const *ptr：同上
- char *const ptr：ptr是常量（ptr不能改变但ptr指向的值可以变）

```C++
char str[] = "hello";
char alt[] = "world";
char* const ptr = str;//const修饰ptr，即指针是常量
*ptr = 'a';//可以
ptr = alt;//报错；不能更改指针
```

- 注意：
  - 字符数组可以用常字符串**初始化**
  - cout<<str;//输出流直接输出字符串，而不是输出首地址。若一定要用cout输出首地址，请先将指针赋值给另一个void*指针，再cout该指针
  
  ```cpp
  char* str = "helloworld";
  std::cout<<str;//输出整个字符串
  void* straddr = str;
  std::cout<<straddr;//输出字符串首地址
  ```
  
  



##### jstring与const char*相互转换

1. const char*转jstring（初始化生成jsring）：

   - 库接口：是`JNIEnv`类的方法

   ```cpp
   jstring NewStringUTF(const char* byte)
   ```

   - 原型：是`JNINativeInterface`结构体提供的方法

   ```cpp
   jstring NewStringUTF(JNIEnv* env, const char* byte)
   ```

2. jstring转const char\*（反向转换为const char\*）：

   - 库接口：是`JNIEnv`类的方法

   ```cpp
   const char* GetStringUTFChars(jstring string, jboolean* isCopy)
   ```

   - 原型：是`JNINativeInterface`结构体提供的方法

   ```cpp
   const char* GetStringUTFChars(JNIEnv* env, jstring string, jboolean* isCopy);
   ```

   `Oracle Java Native API`给出以下解释：

   > ... Returns a pointer to an array of bytes representing the string in modified UTF-8 encoding. This array is valid until it is released by `ReleaseStringUTFChars()`.
   >
   > 
   >
   > If `isCopy` is not `NULL`, then `*isCopy` is set to `JNI_TRUE` if a copy is made; or it is set to `JNI_FALSE` if no copy is made.
   >
   > ...

   值得注意的是：

   1. 不再需要const char*之后，需要通过`ReleaseStringUTFChars()`方法释放
   2. `isCopy()`参数决定是否额外拷贝一份

3. 通过jstring和const jchar\*的相互转换实现jstring和const char\*的相互转换：和以上方法类似，但是是使用`NewString()`和`GetStringChar()`方法。

#### 设计

一个好的日志系统满足几个条件：

- 轻量：依赖项少，体量小，打包整洁，自动清理日志

- 高效：响应速度快，日志保存及时，且占据资源少
- 安全：多线程安全

#### 架构

SCLog原先使用java实现，架构如下：

![SCLog](res/SCLog.png)

#### 待办问题

1. JNI调用jstring的内存占用优化
2. ASE还是其他加密方式？
3. Abseil?
4. map到普通内存区域和ashmem哪个性能会好点



### GMate





## Reference

- Android 四大组件 https://www.jianshu.com/p/51aaa65d5d25
- Android组件化、模块化实现 https://www.jianshu.com/p/a7f256e50d2f
- Android JNI笔记 https://www.jianshu.com/p/87ce6f565d37
- Android NDK官方文档 https://developer.android.google.cn/ndk/guides
- C++ Abseil 概览 https://zhuanlan.zhihu.com/p/29940200
- C++ Google规范 https://google.github.io/styleguide/cppguide.html
- Git 文档全书 https://git-scm.com/book/zh/v2
- Tencent代码规范 https://techmap.woa.com/oteam/8541
- PlantUML类图绘制 https://blog.csdn.net/junhuahouse/article/details/80767632
- JNI 从零开始 https://juejin.cn/post/6844904025662423053
- Java native api 文档 https://docs.oracle.com/javase/7/docs/technotes/guides/jni/spec/functions.html#string_operations

