#include <platon/platon.hpp>

#include <string>
#include <vector>

using namespace std;

class inputParams
{
public:
    inputParams(){}
    inputParams(std::vector<int> vParams)
    {
        myParams = vParams;
    }

public:
    std::vector<int> myParams;
    PLATON_SERIALIZE(inputParams, (myParams))
};


CONTRACT simpleOps: public platon::Contract{
public:
    PLATON_EVENT1(Add, std::string, uint32_t)
    PLATON_EVENT1(call2, std::string, int)
    PLATON_EVENT1(put, std::string, int)
    PLATON_EVENT1(clear, std::string, uint32_t)

    ACTION void init(const inputParams& ipa){
        iParams.self() = ipa;
    }

    CONST std::vector<int> getParams(){
        return iParams.self().myParams;
    }

    CONST int makeCall(){
        std::vector<int> params = iParams.self().myParams;
        int rst = 0;
        for (auto itr = params.begin(); itr != params.end(); ++itr)
        {
            rst += *itr;
        }
        return rst;
    }

    ACTION void putElement(int ele){
        iParams.self().myParams.push_back(ele);
        PLATON_EMIT_EVENT1(put, "putElement" , ele);
    }

    ACTION void clearElement(){
        if (!iParams.self().myParams.empty())
        {
            iParams.self().myParams.clear();
        }
        uint32_t returnValue = 73;
        PLATON_EMIT_EVENT1(clear, "clearElement" , returnValue);
    }

    ACTION int AddCalc(){
        int rst = 0;
        for (auto itr = iParams.self().myParams.begin(); itr != iParams.self().myParams.end(); ++itr)
        {
            rst += *itr;
        }

        PLATON_EMIT_EVENT1(Add, "AddCalc", rst);
        return rst;
    }

    CONST int makeCall2(int a, int b){
        int c = a + b;
        PLATON_EMIT_EVENT1(call2, "makeCall2", c);
        return c;
    }

private:
    platon::StorageType<"Params"_n, inputParams> iParams;
};

PLATON_DISPATCH(simpleOps, (init)(getParams)(makeCall)(putElement)(clearElement)(AddCalc)(makeCall2))
