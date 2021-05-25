#include <platon/platon.hpp>

#include <list>

CONTRACT Simple: public platon::Contract
{
private:
    platon::StorageType<"mylist"_n, std::list<int>> info;
    platon::StorageType<"myNumber"_n, int> cur;

    PLATON_EVENT2(Add, std::string , int);

public:
    ACTION void init()
    {
        cur.self() = 1;
    }

    ACTION void makeNumber()
    {
        info.self().push_back(++cur.self());
    }

    ACTION void deleteNumber()
    {
        info.self().pop_front();
    }

    CONST std::list<int> get_Numbers()
    {
        return info.self();
    }

    ACTION int calcAdd(int a, int b)
    {
        //auto sender = platon::platon_caller();
        //std::list<int> lv;
        //lv.push_back(a+b);
        auto c = a + b;
        PLATON_EMIT_EVENT1(Add, "calcAdd", c);

        return c;
    }
};

PLATON_DISPATCH(Simple, (init)(makeNumber)(deleteNumber)(get_Numbers)(calcAdd))
